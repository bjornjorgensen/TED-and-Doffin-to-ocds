# converters/bt_106_procedure.py

import logging
from lxml import etree
from typing import Any

logger = logging.getLogger(__name__)

# Constants
XPATH_PROCEDURE_ACCELERATED = "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReasonCode"
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


def parse_boolean_value(value: str) -> bool | None:
    """
    Parse a string value into a boolean.

    Args:
        value: The string value to parse.

    Returns:
        Optional[bool]: The parsed boolean value, or None if invalid.
    """
    cleaned_value = value.strip().lower()
    if cleaned_value in VALID_TRUE_VALUES:
        return True
    if cleaned_value in VALID_FALSE_VALUES:
        return False
    return None


def parse_procedure_accelerated(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the XML content to extract the procedure acceleration information.

    Args:
        xml_content: The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the parsed procedure
        acceleration data, or None if no relevant data is found.

    Raises:
        ValueError: If the input is invalid.
        etree.XMLSyntaxError: If the XML is malformed.
    """
    try:
        xml_content = validate_xml_content(xml_content)
        root = etree.fromstring(xml_content)

        # Check if the relevant XPath exists
        procedure_elements = root.xpath(
            XPATH_PROCEDURE_ACCELERATED, namespaces=NAMESPACES
        )
        if not procedure_elements:
            logger.info(
                "No procedure acceleration data found. Skipping parse_procedure_accelerated."
            )
            return None

        # Get the acceleration status
        acceleration_value = procedure_elements[0].text
        if not acceleration_value:
            logger.info("Empty acceleration value found")
            return None

        # Parse the boolean value
        is_accelerated = parse_boolean_value(acceleration_value)
        if is_accelerated is None:
            logger.warning("Invalid acceleration value: %s", acceleration_value)
            return None

        logger.debug(
            "Parsed acceleration value: %s -> %s", acceleration_value, is_accelerated
        )

    except (ValueError, etree.XMLSyntaxError):
        logger.exception("Error parsing procedure acceleration")
        raise
    except Exception:
        logger.exception("Unexpected error parsing procedure acceleration")
        raise
    else:
        return {"tender": {"procedure": {"isAccelerated": is_accelerated}}}


def merge_procedure_accelerated(
    release_json: dict[str, Any], procedure_accelerated_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed procedure acceleration data into the main OCDS release JSON.

    Args:
        release_json: The main OCDS release JSON to be updated.
        procedure_accelerated_data: The parsed procedure acceleration data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not isinstance(release_json, dict):
        logger.error("Invalid release_json type: %s", type(release_json))
        raise TypeError(ERR_INVALID_RELEASE_JSON)

    if not procedure_accelerated_data:
        logger.info("No procedure acceleration data to merge")
        return

    tender = release_json.setdefault("tender", {})
    procedure = tender.setdefault("procedure", {})

    try:
        is_accelerated = procedure_accelerated_data["tender"]["procedure"][
            "isAccelerated"
        ]
        if isinstance(is_accelerated, bool):
            procedure["isAccelerated"] = is_accelerated
            logger.debug("Set procedure acceleration to: %s", is_accelerated)
            logger.info("Successfully merged procedure acceleration data")
        else:
            logger.warning("Invalid acceleration value type: %s", type(is_accelerated))
    except KeyError:
        logger.warning("Missing required keys in procedure_accelerated_data")
