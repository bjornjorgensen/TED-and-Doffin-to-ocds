import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Constants for TED XPaths
XPATH_F01_FRAMEWORK_JUSTIFICATION = (
    "//TED_EXPORT/FORM_SECTION/F01_2014/PROCEDURE/FRAMEWORK/JUSTIFICATION/text()"
)
XPATH_F02_FRAMEWORK_JUSTIFICATION = (
    "//TED_EXPORT/FORM_SECTION/F02_2014/PROCEDURE/FRAMEWORK/JUSTIFICATION/text()"
)
XPATH_F04_FRAMEWORK_JUSTIFICATION = (
    "//TED_EXPORT/FORM_SECTION/F04_2014/PROCEDURE/FRAMEWORK/JUSTIFICATION/text()"
)
XPATH_F05_FRAMEWORK_JUSTIFICATION = (
    "//TED_EXPORT/FORM_SECTION/F05_2014/PROCEDURE/FRAMEWORK/JUSTIFICATION/text()"
)
XPATH_F17_FRAMEWORK_JUSTIFICATION = "//TED_EXPORT/FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/OBJECT_CONTRACT_INFORMATION_DEFENCE/DESCRIPTION_CONTRACT_INFORMATION_DEFENCE/F17_FRAMEWORK/JUSTIFICATION/text()"
XPATH_F19_FRAMEWORK_JUSTIFICATION = "//TED_EXPORT/FORM_SECTION/CONTRACT_CONCESSIONAIRE_DEFENCE/FD_CONTRACT_CONCESSIONAIRE_DEFENCE/OBJECT_CONTRACT_SUB_DEFENCE/DESCRIPTION_CONTRACT_SUB_DEFENCE/F19_FRAMEWORK/JUSTIFICATION/text()"
XPATH_F21_FRAMEWORK_JUSTIFICATION = (
    "//TED_EXPORT/FORM_SECTION/F21_2014/PROCEDURE/FRAMEWORK/JUSTIFICATION/text()"
)
XPATH_F22_FRAMEWORK_JUSTIFICATION = (
    "//TED_EXPORT/FORM_SECTION/F22_2014/PROCEDURE/FRAMEWORK/JUSTIFICATION/text()"
)

# All possible XPaths combined
ALL_FRAMEWORK_JUSTIFICATION_XPATHS = [
    XPATH_F01_FRAMEWORK_JUSTIFICATION,
    XPATH_F02_FRAMEWORK_JUSTIFICATION,
    XPATH_F04_FRAMEWORK_JUSTIFICATION,
    XPATH_F05_FRAMEWORK_JUSTIFICATION,
    XPATH_F17_FRAMEWORK_JUSTIFICATION,
    XPATH_F19_FRAMEWORK_JUSTIFICATION,
    XPATH_F21_FRAMEWORK_JUSTIFICATION,
    XPATH_F22_FRAMEWORK_JUSTIFICATION,
]

# Error messages
ERR_EMPTY_XML = "XML content cannot be None or empty"
ERR_INVALID_RELEASE_JSON = "release_json must be a dictionary"


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


def parse_framework_duration_justification(xml_content: str | bytes) -> dict | None:
    """Parse framework agreement duration justification from TED XML.

    Extract information about justification for exceptional cases when the duration
    of framework agreements exceeds the legal limits as defined in BT-109.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "techniques": {
                    "frameworkAgreement": {
                        "periodRationale": str
                    }
                }
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
        ValueError: If the XML content is empty or None.
    """
    xml_content = validate_xml_content(xml_content)
    root = etree.fromstring(xml_content)

    # Try all possible XPaths
    for xpath in ALL_FRAMEWORK_JUSTIFICATION_XPATHS:
        justification_elements = root.xpath(xpath)
        if justification_elements and justification_elements[0].strip():
            justification_text = justification_elements[0].strip()
            return {
                "tender": {
                    "techniques": {
                        "frameworkAgreement": {"periodRationale": justification_text}
                    }
                }
            }

    logger.debug("No framework duration justification found in TED XML")
    return None


def merge_framework_duration_justification(
    release_json: dict, framework_justification_data: dict | None
) -> None:
    """Merge framework duration justification data into the OCDS release.

    Updates the release JSON in-place by adding or updating framework agreement
    information.

    Args:
        release_json: The main OCDS release JSON to be updated.
        framework_justification_data: The parsed framework justification data
            in the same format as returned by parse_framework_duration_justification().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    Raises:
        TypeError: If release_json is not a dictionary.
    """
    if not isinstance(release_json, dict):
        raise TypeError(ERR_INVALID_RELEASE_JSON)

    if not framework_justification_data:
        logger.info("No framework duration justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    techniques = tender.setdefault("techniques", {})
    framework = techniques.setdefault("frameworkAgreement", {})

    # Set the periodRationale from the parsed data
    framework["periodRationale"] = framework_justification_data["tender"]["techniques"][
        "frameworkAgreement"
    ]["periodRationale"]

    logger.info("Successfully merged TED framework duration justification data")
