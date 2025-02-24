# converters/bt_106_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Constants
XPATH_PROCEDURE_ACCELERATED = "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReasonCode/text()"
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
    as defined in BT-106.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "procedure": {
                    "isAccelerated": bool
                }
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    procedure_elements = root.xpath(XPATH_PROCEDURE_ACCELERATED, namespaces=namespaces)
    if not procedure_elements:
        return None

    acceleration_value = procedure_elements[0].strip()
    is_accelerated = acceleration_value.lower() in {"true", "1", "yes"}
    result = {"tender": {"procedure": {"isAccelerated": is_accelerated}}}
    if is_accelerated:
        result["tender"]["procedure"]["acceleratedRationale"] = acceleration_value
    return result


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
        procedure["isAccelerated"] = procedure_accelerated_data["tender"]["procedure"][
            "isAccelerated"
        ]
        if "acceleratedRationale" in procedure_accelerated_data["tender"]["procedure"]:
            procedure["acceleratedRationale"] = procedure_accelerated_data["tender"][
                "procedure"
            ]["acceleratedRationale"]
        logger.info("Successfully merged procedure acceleration data")
