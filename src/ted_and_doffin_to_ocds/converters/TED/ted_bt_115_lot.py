import logging

from lxml import etree

logger = logging.getLogger(__name__)

# XPath constants for different TED form types
XPATH_F01_GPA_COVERAGE = "//TED_EXPORT/FORM_SECTION/F01_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()"
XPATH_F02_GPA_COVERAGE = (
    "//TED_EXPORT/FORM_SECTION/F02_2014/PROCEDURE/CONTRACT_COVERED_GPA/text()"
)
XPATH_F03_GPA_COVERAGE = "//TED_EXPORT/FORM_SECTION/F03_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()"
XPATH_F04_GPA_COVERAGE = "//TED_EXPORT/FORM_SECTION/F04_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()"
XPATH_F05_GPA_COVERAGE = "//TED_EXPORT/FORM_SECTION/F05_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()"
XPATH_F15_GPA_COVERAGE = "//TED_EXPORT/FORM_SECTION/F15_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()"
XPATH_F24_GPA_COVERAGE = "//TED_EXPORT/FORM_SECTION/F24_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()"
XPATH_F25_GPA_COVERAGE = "//TED_EXPORT/FORM_SECTION/F25_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()"

# All possible XPaths combined
ALL_GPA_COVERAGE_XPATHS = [
    XPATH_F01_GPA_COVERAGE,
    XPATH_F02_GPA_COVERAGE,
    XPATH_F03_GPA_COVERAGE,
    XPATH_F04_GPA_COVERAGE,
    XPATH_F05_GPA_COVERAGE,
    XPATH_F15_GPA_COVERAGE,
    XPATH_F24_GPA_COVERAGE,
    XPATH_F25_GPA_COVERAGE,
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


def parse_gpa_coverage(xml_content: str | bytes) -> dict | None:
    """Parse GPA coverage information from TED XML.

    Extract information about whether the procurement is covered by the
    Government Procurement Agreement (GPA) as defined in BT-115.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "coveredBy": ["GPA"]  # Only present if GPA covered
            }
        }
        Returns None if no relevant data is found or if GPA is not covered.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
        ValueError: If the XML content is empty or None.
    """
    xml_content = validate_xml_content(xml_content)
    root = etree.fromstring(xml_content)

    # Try all possible XPaths
    for xpath in ALL_GPA_COVERAGE_XPATHS:
        gpa_coverage_elements = root.xpath(xpath)
        if gpa_coverage_elements and gpa_coverage_elements[0].strip().lower() == "yes":
            return {"tender": {"coveredBy": ["GPA"]}}

    logger.debug("No GPA coverage found in TED XML or GPA is not covered")
    return None


def merge_gpa_coverage(release_json: dict, gpa_coverage_data: dict | None) -> None:
    """Merge GPA coverage data into the OCDS release.

    Updates the release JSON in-place by adding or updating GPA coverage information.

    Args:
        release_json: The main OCDS release JSON to be updated.
        gpa_coverage_data: The parsed GPA coverage data
            in the same format as returned by parse_gpa_coverage().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    Raises:
        TypeError: If release_json is not a dictionary.
    """
    if not isinstance(release_json, dict):
        raise TypeError(ERR_INVALID_RELEASE_JSON)

    if not gpa_coverage_data:
        logger.info("No GPA coverage data to merge")
        return

    tender = release_json.setdefault("tender", {})
    covered_by = tender.setdefault("coveredBy", [])

    # Add "GPA" to coveredBy array if not already present
    if "GPA" not in covered_by:
        covered_by.append("GPA")

    logger.info("Successfully merged TED GPA coverage data")
