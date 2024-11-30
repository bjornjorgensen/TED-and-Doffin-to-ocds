# converters/bt_105_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# Constants for XML processing
XPATH_PROCEDURE_CODE = (
    "//cac:TenderingProcess/cbc:ProcedureCode[@listName='procurement-procedure-type']"
)
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
    "oth-mult": None,
    "oth-single": None,
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
    """
    Validate and prepare XML content for processing.

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


def parse_procedure_type(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the XML content to extract the procedure type information.

    Args:
        xml_content: The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the parsed procedure type data,
        or None if no relevant data is found.

    Raises:
        ValueError: If the input is invalid.
        etree.XMLSyntaxError: If the XML is malformed.
    """
    try:
        xml_content = validate_xml_content(xml_content)
        root = etree.fromstring(xml_content)

        # Check if the relevant XPath exists
        procedure_elements = root.xpath(XPATH_PROCEDURE_CODE, namespaces=NAMESPACES)
        if not procedure_elements:
            logger.info("No procedure type data found. Skipping parse_procedure_type.")
            return None

        # Get the procedure code
        procedure_code = procedure_elements[0].text
        if not procedure_code:
            logger.info("Empty procedure code found")
            return None

        code = procedure_code.strip().lower()
        if code not in PROCEDURE_CODE_MAPPING:
            logger.warning("Unknown procedure code: %s", code)
            return None

        result = {"tender": {}}

        # Map the procedure method
        procurement_method = PROCEDURE_CODE_MAPPING.get(code)
        if procurement_method:
            result["tender"]["procurementMethod"] = procurement_method
            logger.debug(
                "Mapped procedure code %s to method %s", code, procurement_method
            )

        # Map the procedure details
        procurement_method_details = PROCEDURE_DETAILS_MAPPING.get(code)
        if procurement_method_details:
            result["tender"]["procurementMethodDetails"] = procurement_method_details
            logger.debug("Added procedure details for code %s", code)

        return result if result["tender"] else None

    except (ValueError, etree.XMLSyntaxError):
        logger.exception("Error parsing procedure type")
        raise
    except Exception:
        logger.exception("Unexpected error parsing procedure type")
        raise


def merge_procedure_type(
    release_json: dict[str, Any], procedure_type_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed procedure type data into the main OCDS release JSON.

    Args:
        release_json: The main OCDS release JSON to be updated.
        procedure_type_data: The parsed procedure type data to be merged.

    Returns:
        None: The function updates the release_json in-place.
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
