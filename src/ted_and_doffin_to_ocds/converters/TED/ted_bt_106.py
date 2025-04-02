import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Constants for TED
XPATH_F02_PROCEDURE_ACCELERATED = (
    "//TED_EXPORT/FORM_SECTION/F02_2014/PROCEDURE/ACCELERATED_PROC/text()"
)
XPATH_F03_PROCEDURE_ACCELERATED = (
    "//TED_EXPORT/FORM_SECTION/F03_2014/PROCEDURE/ACCELERATED_PROC/text()"
)

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


def parse_procedure_accelerated(xml_content: str | bytes) -> dict | None:
    """Parse procedure acceleration information from TED XML.

    Extract information about whether the time limit can be reduced due to urgency
    as defined in BT-106 for TED format.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "procedure": {
                    "isAccelerated": bool,
                    "acceleratedRationale": str  # If the rationale is included in the text
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

    # Try both F02 and F03 forms
    for xpath in [XPATH_F02_PROCEDURE_ACCELERATED, XPATH_F03_PROCEDURE_ACCELERATED]:
        procedure_elements = root.xpath(xpath)
        if procedure_elements:
            # In TED, the presence of the element indicates acceleration is true
            # The element content often contains the rationale
            content = procedure_elements[0].strip()

            result = {"tender": {"procedure": {"isAccelerated": True}}}

            # If the element has content, use it as the rationale
            if content:
                result["tender"]["procedure"]["acceleratedRationale"] = content

            return result

    logger.debug("No accelerated procedure information found in TED XML")
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

    if not isinstance(release_json, dict):
        raise TypeError(ERR_INVALID_RELEASE_JSON)

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

    logger.info("Successfully merged TED procedure acceleration data")
