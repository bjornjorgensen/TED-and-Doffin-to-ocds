# converters/bt_105_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Constants for XML processing
XPATH_PROCEDURE_CODE = "//cac:TenderingProcess/cbc:ProcedureCode[@listName='procurement-procedure-type']/text()"
NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

# Error messages
ERR_EMPTY_XML = "XML content cannot be None or empty"
ERR_INVALID_RELEASE_JSON = "release_json must be a dictionary"

# Mapping dictionaries
PROCEDURE_CODE_MAPPING = {
    "open": "open",
    "restricted": "selective",
    "comp-dial": "selective",
    "comp-tend": "selective",
    "innovation": "selective",
    "neg-w-call": "selective",
    "neg-wo-call": "limited",
    "exp-int-rail": "selective",
    # No mapping for these codes - they get None
    # "oth-mult": None,
    # "oth-single": None,
}

PROCEDURE_DETAILS_MAPPING = {
    "open": "Open procedure",
    "restricted": "Restricted procedure",
    "comp-dial": "Competitive dialogue",
    "comp-tend": "Competitive tendering (article 5(3) of Regulation 1370/2007)",
    "innovation": "Innovation partnership",
    "neg-w-call": "Negotiated with prior publication of a call for competition / competitive with negotiation",
    "neg-wo-call": "Negotiated without prior call for competition",
    "exp-int-rail": "Request for expression of interest – only for rail (article 5(3b) of Regulation 1370/2007)",
    "oth-mult": "Other multiple stage procedure",
    "oth-single": "Other single stage procedure",
}


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


def parse_procedure_type(xml_content: str | bytes) -> dict | None:
    """Parse procurement procedure type information from XML.

    Extract information about the type of procurement procedure as defined in BT-105.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "procurementMethod": str,  # Only for mapped codes
                "procurementMethodDetails": str
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    procedure_elements = root.xpath(XPATH_PROCEDURE_CODE, namespaces=NAMESPACES)

    if not procedure_elements:
        return None

    code = procedure_elements[0].strip().lower()
    result = {"tender": {}}

    # Add procurementMethod only if we have a mapping
    if code in PROCEDURE_CODE_MAPPING:
        result["tender"]["procurementMethod"] = PROCEDURE_CODE_MAPPING[code]

    # Always add procurementMethodDetails if available
    if code in PROCEDURE_DETAILS_MAPPING:
        result["tender"]["procurementMethodDetails"] = PROCEDURE_DETAILS_MAPPING[code]

    return result if result["tender"] else None


def merge_procedure_type(release_json: dict, procedure_type_data: dict | None) -> None:
    """Merge procedure type data into the OCDS release.

    Updates the release JSON in-place by adding or updating procurement method information.

    Args:
        release_json: The main OCDS release JSON to be updated.
        procedure_type_data: The parsed procedure type data
            in the same format as returned by parse_procedure_type().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not isinstance(release_json, dict):
        logger.error("Invalid release_json type: %s", type(release_json))
        raise TypeError(ERR_INVALID_RELEASE_JSON)

    if not procedure_type_data:
        logger.info("No procedure type data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender_data = procedure_type_data.get("tender", {})

    if "procurementMethod" in tender_data:
        tender["procurementMethod"] = tender_data["procurementMethod"]
        logger.debug("Set procurement method to: %s", tender_data["procurementMethod"])

    if "procurementMethodDetails" in tender_data:
        tender["procurementMethodDetails"] = tender_data["procurementMethodDetails"]
        logger.debug(
            "Set procurement method details to: %s",
            tender_data["procurementMethodDetails"],
        )

    logger.info("Successfully merged procedure type data")
