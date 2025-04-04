import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_gpa_coverage_part(xml_content: str | bytes) -> dict | None:
    """Parse GPA coverage information from TED XML for the part.

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
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    # Check for GPA coverage in different TED form types
    gpa_paths = [
        "//TED_EXPORT/FORM_SECTION/F01_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()",
        "//TED_EXPORT/FORM_SECTION/F04_2014/PROCEDURE/*[matches(name(),'CONTRACT_COVERED_GPA')]/text()",
        # Add more paths for other form types if needed
    ]

    for path in gpa_paths:
        gpa_coverage = root.xpath(path)
        if gpa_coverage:
            # TED typically uses 'YES' or 'NO' for boolean values
            if gpa_coverage[0].upper() == "YES":
                return {"tender": {"coveredBy": ["GPA"]}}
            return None

    return None


def merge_gpa_coverage_part(
    release_json: dict, gpa_coverage_part_data: dict | None
) -> None:
    """Merge GPA coverage part data into the OCDS release.

    Updates the release JSON in-place by adding GPA coverage information
    to the tender.

    Args:
        release_json: The main OCDS release JSON to be updated.
        gpa_coverage_part_data: The parsed GPA coverage data
            in the same format as returned by parse_gpa_coverage_part().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not gpa_coverage_part_data:
        logger.info("No GPA coverage part data to merge")
        return

    tender = release_json.setdefault("tender", {})

    if "coveredBy" in gpa_coverage_part_data["tender"]:
        tender.setdefault("coveredBy", []).extend(
            gpa_coverage_part_data["tender"]["coveredBy"]
        )
        logger.info("Merged GPA coverage part data")
