import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tool_atypical_url_part(xml_content: str | bytes) -> dict | None:
    """Parse atypical tool URL information from TED XML for the part (BT-124).

    Extract information about URLs for tools and devices that are not generally
    available as defined in BT-124. Maps to `tender.communication.atypicalToolUrl`.

    Args:
        xml_content: The TED XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "communication": {
                    "atypicalToolUrl": str
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

    # TED XML paths for different form types based on the prompt
    form_paths = [
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F01_2014']/*[local-name()='CONTRACTING_BODY']/*[local-name()='URL_TOOL']",
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F04_2014']/*[local-name()='CONTRACTING_BODY']/*[local-name()='URL_TOOL']",
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F21_2014']/*[local-name()='CONTRACTING_BODY']/*[local-name()='URL_TOOL']",
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F22_2014']/*[local-name()='CONTRACTING_BODY']/*[local-name()='URL_TOOL']",
    ]

    for path in form_paths:
        url_elements = root.xpath(path)
        if url_elements:
            return {
                "tender": {"communication": {"atypicalToolUrl": url_elements[0].text}}
            }

    return None


def merge_tool_atypical_url_part(
    release_json: dict, atypical_url_data: dict | None
) -> None:
    """Merge atypical tool URL part data into the OCDS release.

    Updates the release JSON in-place by adding or updating communication information
    in the tender.

    Args:
        release_json: The main OCDS release JSON to be updated.
        atypical_url_data: The parsed atypical tool URL data
            in the same format as returned by parse_tool_atypical_url_part().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not atypical_url_data:
        logger.info("No atypical tool URL part data to merge")
        return

    tender = release_json.setdefault("tender", {})

    if "communication" in atypical_url_data["tender"]:
        communication = tender.setdefault("communication", {})
        communication["atypicalToolUrl"] = atypical_url_data["tender"]["communication"][
            "atypicalToolUrl"
        ]
        logger.info("Merged atypical tool URL part data")
