import logging

from lxml import etree

logger = logging.getLogger(__name__)

# XPath constants for different TED form types
XPATH_F01_MAX_PARTICIPANTS = (
    "//TED_EXPORT/FORM_SECTION/F01_2014/PROCEDURE/FRAMEWORK/NB_PARTICIPANTS/text()"
)
XPATH_F02_MAX_PARTICIPANTS = (
    "//TED_EXPORT/FORM_SECTION/F02_2014/PROCEDURE/FRAMEWORK/NB_PARTICIPANTS/text()"
)
XPATH_F04_MAX_PARTICIPANTS = (
    "//TED_EXPORT/FORM_SECTION/F04_2014/PROCEDURE/FRAMEWORK/NB_PARTICIPANTS/text()"
)
XPATH_F05_MAX_PARTICIPANTS = (
    "//TED_EXPORT/FORM_SECTION/F05_2014/PROCEDURE/FRAMEWORK/NB_PARTICIPANTS/text()"
)
XPATH_F17_MAX_PARTICIPANTS = "//TED_EXPORT/FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/OBJECT_CONTRACT_INFORMATION_DEFENCE/DESCRIPTION_CONTRACT_INFORMATION_DEFENCE/F17_FRAMEWORK/SEVERAL_OPERATORS/MAX_NUMBER_PARTICIPANTS/text()"
XPATH_F19_MAX_PARTICIPANTS = "//TED_EXPORT/FORM_SECTION/CONTRACT_CONCESSIONAIRE_DEFENCE/FD_CONTRACT_CONCESSIONAIRE_DEFENCE/OBJECT_CONTRACT_SUB_DEFENCE/DESCRIPTION_CONTRACT_SUB_DEFENCE/F19_FRAMEWORK/SEVERAL_OPERATORS/MAX_NUMBER_PARTICIPANTS/text()"

# All possible XPaths combined
ALL_MAX_PARTICIPANTS_XPATHS = [
    XPATH_F01_MAX_PARTICIPANTS,
    XPATH_F02_MAX_PARTICIPANTS,
    XPATH_F04_MAX_PARTICIPANTS,
    XPATH_F05_MAX_PARTICIPANTS,
    XPATH_F17_MAX_PARTICIPANTS,
    XPATH_F19_MAX_PARTICIPANTS,
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


def parse_framework_max_participants(xml_content: str | bytes) -> dict | None:
    """Parse framework agreement maximum participants from TED XML.

    Extract information about the maximum number of participants in the framework agreement
    as defined in BT-113.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "techniques": {
                    "frameworkAgreement": {
                        "maximumParticipants": int
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
    for xpath in ALL_MAX_PARTICIPANTS_XPATHS:
        max_participants_elements = root.xpath(xpath)
        if max_participants_elements and max_participants_elements[0].strip():
            try:
                max_participants = int(max_participants_elements[0].strip())
            except ValueError:
                logger.warning(
                    "Invalid maximum participants value: %s",
                    max_participants_elements[0].strip(),
                )
            else:
                return {
                    "tender": {
                        "techniques": {
                            "frameworkAgreement": {
                                "maximumParticipants": max_participants
                            }
                        }
                    }
                }

    logger.debug("No framework maximum participants found in TED XML")
    return None


def merge_framework_max_participants(
    release_json: dict, framework_max_participants_data: dict | None
) -> None:
    """Merge framework maximum participants data into the OCDS release.

    Updates the release JSON in-place by adding or updating framework agreement
    information.

    Args:
        release_json: The main OCDS release JSON to be updated.
        framework_max_participants_data: The parsed maximum participants data
            in the same format as returned by parse_framework_max_participants().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    Raises:
        TypeError: If release_json is not a dictionary.
    """
    if not isinstance(release_json, dict):
        raise TypeError(ERR_INVALID_RELEASE_JSON)

    if not framework_max_participants_data:
        logger.info("No framework maximum participants data to merge")
        return

    tender = release_json.setdefault("tender", {})
    techniques = tender.setdefault("techniques", {})
    framework = techniques.setdefault("frameworkAgreement", {})

    # Set the maximumParticipants from the parsed data
    framework["maximumParticipants"] = framework_max_participants_data["tender"][
        "techniques"
    ]["frameworkAgreement"]["maximumParticipants"]

    logger.info("Successfully merged TED framework maximum participants data")
