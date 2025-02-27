# converters/bt_106_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Constants
XPATH_PROCEDURE_ACCELERATED = "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReasonCode/text()"
XPATH_PROCEDURE_RATIONALE = "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReason/text()"
NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

# Error messages
ERR_EMPTY_XML = "XML content cannot be None or empty"
ERR_INVALID_RELEASE_JSON = "release_json must be a dictionary"

# Valid values
VALID_TRUE_VALUES = {"true", "1", "yes"}
VALID_FALSE_VALUES = {"false", "0", "no"}


def validate_xml_content(xml_content: str | bytes) -> bytes:
    """Validate and prepare XML content for processing.

    Args:
        xml_content: The XML content to validate.

    Returns:
        bytes: The validated XML content.

    Raises:
        ValueError: If the input is None or empty.
        etree.XMLSyntaxError: If the XML is malformed.

    """
    if not xml_content:
        raise ValueError(ERR_EMPTY_XML)

    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Invalid XML content")
        raise

    return xml_content


def parse_procedure_accelerated(xml_content: str | bytes) -> dict | None:
    """Parse procedure acceleration information from XML.

    Extract information about whether the time limit can be reduced due to urgency
    as defined in BT-106. This field indicates whether receipt of requests to participate
    or tenders can be reduced due to a state of urgency.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "procedure": {
                    "isAccelerated": bool,
                    "acceleratedRationale": str  # Optional, only present if isAccelerated is True
                }
            }
        }
        Returns None if no relevant data is found or if the data is invalid.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
        ValueError: If the XML content is empty or None.
    """
    xml_content = validate_xml_content(xml_content)
    root = etree.fromstring(xml_content)

    procedure_elements = root.xpath(XPATH_PROCEDURE_ACCELERATED, namespaces=NAMESPACES)
    if not procedure_elements:
        logger.debug("No accelerated procedure information found in XML")
        return None

    acceleration_value = procedure_elements[0].strip()
    acceleration_value_lower = acceleration_value.lower()
    
    if acceleration_value_lower in VALID_TRUE_VALUES:
        is_accelerated = True
        result = {"tender": {"procedure": {"isAccelerated": is_accelerated}}}
        
        rationale_elements = root.xpath(XPATH_PROCEDURE_RATIONALE, namespaces=NAMESPACES)
        if rationale_elements and rationale_elements[0].strip():
            result["tender"]["procedure"]["acceleratedRationale"] = rationale_elements[0].strip()
        
        return result
    
    if acceleration_value_lower in VALID_FALSE_VALUES:
        return {"tender": {"procedure": {"isAccelerated": False}}}
    
    logger.warning("Invalid acceleration value '%s'. Must be one of %s",
                acceleration_value, VALID_TRUE_VALUES | VALID_FALSE_VALUES)
    return None


def merge_procedure_accelerated(
    release_json: dict, procedure_accelerated_data: dict | None
) -> None:
    """Merge procedure acceleration data into the OCDS release.

    Updates the release JSON in-place by adding or updating procedure information.

    Args:
        release_json: The main OCDS release JSON to be updated.
        procedure_accelerated_data: The parsed procedure acceleration data
            in the same format as returned by parse_procedure_accelerated().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not procedure_accelerated_data:
        logger.info("No procedure acceleration data to merge")
        return

    tender = release_json.setdefault("tender", {})
    procedure = tender.setdefault("procedure", {})

    if "isAccelerated" in procedure_accelerated_data["tender"]["procedure"]:
        is_accelerated = procedure_accelerated_data["tender"]["procedure"]["isAccelerated"]
        procedure["isAccelerated"] = is_accelerated
        
        # Only include acceleratedRationale if procedure is actually accelerated
        if is_accelerated and "acceleratedRationale" in procedure_accelerated_data["tender"]["procedure"]:
            procedure["acceleratedRationale"] = procedure_accelerated_data["tender"]["procedure"]["acceleratedRationale"]
        elif "acceleratedRationale" in procedure:
            # Remove any existing acceleratedRationale if procedure is not accelerated
            del procedure["acceleratedRationale"]
            
        logger.info("Successfully merged procedure acceleration data")
