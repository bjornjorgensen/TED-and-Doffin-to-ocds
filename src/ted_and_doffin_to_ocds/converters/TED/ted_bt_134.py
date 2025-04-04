import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bid_opening_description(xml_content: str | bytes) -> dict | None:
    """Parse the public opening description information from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse

    Returns:
        Optional[Dict]: Dictionary containing tender bidOpening description information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "bidOpening": {
                    "description": str
                }
            }
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    # Try to extract public opening description from both F02 and F05 form types
    xpath_queries = [
        "//*[local-name()='OPENING_CONDITION']/*[local-name()='INFO_ADD']/text()",
        "//*[local-name()='PROCEDURE']/*[local-name()='OPENING_CONDITION']/*[local-name()='INFO_ADD']/text()",
        "//*[local-name()='F02_2014']/*[local-name()='PROCEDURE']/*[local-name()='OPENING_CONDITION']/*[local-name()='INFO_ADD']/text()",
        "//*[local-name()='F05_2014']/*[local-name()='PROCEDURE']/*[local-name()='OPENING_CONDITION']/*[local-name()='INFO_ADD']/text()",
    ]

    for xpath_query in xpath_queries:
        descriptions = root.xpath(xpath_query)
        if descriptions and descriptions[0].strip():
            return {"tender": {"bidOpening": {"description": descriptions[0].strip()}}}

    return None


def merge_bid_opening_description(
    release_json: dict, bid_opening_data: dict | None
) -> None:
    """Merge bid opening description data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        bid_opening_data (Optional[Dict]): The source data containing bid opening description
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.bidOpening.description field.

    """
    if not bid_opening_data:
        logger.debug("No bid opening description data to merge")
        return

    if (
        "tender" not in bid_opening_data
        or "bidOpening" not in bid_opening_data["tender"]
    ):
        logger.warning("Invalid bid opening description data structure")
        return

    release_json.setdefault("tender", {}).setdefault("bidOpening", {}).update(
        {"description": bid_opening_data["tender"]["bidOpening"]["description"]}
    )

    logger.info("Merged bid opening description data")
