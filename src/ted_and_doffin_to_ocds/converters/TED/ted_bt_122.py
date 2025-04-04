import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_electronic_auction_description(xml_content: str | bytes) -> dict | None:
    """Parse electronic auction description from TED XML.

    Extract additional information about the electronic auction as defined in BT-122.
    Note: TED forms provide this information at the procedure level, not per lot.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "techniques": {
                    "electronicAuction": {
                        "description": str
                    }
                }
            }
        }
        Returns None if the description is not present.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    # Define XPaths for different TED forms
    # Note: The defence form path seems related to *use* not description, sticking to F01/F02/F04/F05
    xpath_expressions = [
        "TED_EXPORT/FORM_SECTION/F01_2014/PROCEDURE/INFO_ADD_EAUCTION",
        "TED_EXPORT/FORM_SECTION/F02_2014/PROCEDURE/INFO_ADD_EAUCTION",
        "TED_EXPORT/FORM_SECTION/F04_2014/PROCEDURE/INFO_ADD_EAUCTION",
        "TED_EXPORT/FORM_SECTION/F05_2014/PROCEDURE/INFO_ADD_EAUCTION",
    ]

    description_text = None
    for xpath in xpath_expressions:
        elements = root.xpath(f"//{xpath}")
        if elements:
            # Extract text content, joining if multiple paragraphs exist
            description_text = "\n".join(
                p.text for p in elements[0].xpath("./P") if p.text
            ).strip()
            if description_text:
                break  # Found description in one of the forms

    if description_text:
        return {
            "tender": {
                "techniques": {"electronicAuction": {"description": description_text}}
            }
        }

    return None


def merge_electronic_auction_description(
    release_json: dict, auction_description_data: dict | None
) -> None:
    """Merge electronic auction description data into the OCDS release.

    Updates the release JSON in-place by adding or updating electronic auction
    information at the tender level.

    Args:
        release_json: The main OCDS release JSON to be updated.
        auction_description_data: The parsed auction description data
            in the same format as returned by parse_electronic_auction_description().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not auction_description_data:
        logger.info("No electronic auction description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    techniques = tender.setdefault("techniques", {})
    electronic_auction = techniques.setdefault("electronicAuction", {})

    if (
        "techniques" in auction_description_data["tender"]
        and "electronicAuction" in auction_description_data["tender"]["techniques"]
    ):
        description = auction_description_data["tender"]["techniques"][
            "electronicAuction"
        ].get("description")
        if description:
            electronic_auction["description"] = description
            logger.info("Merged electronic auction description at tender level")
        else:
            logger.info("No description found in auction data to merge")
    else:
        logger.info("No electronic auction data found in parsed data to merge")
