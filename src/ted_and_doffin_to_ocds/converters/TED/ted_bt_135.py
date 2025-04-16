import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_direct_award_justification_rationale(xml_content: str | bytes) -> dict | None:
    """Parse the direct award justification text (BT-135) from TED XML content.

    Maps to tender.procurementMethodRationale in OCDS.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse

    Returns:
        Optional[Dict]: Dictionary containing tender procurement method rationale, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "procurementMethodRationale": str
            }
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    # Try to extract direct award justification from multiple TED form types based on BT-135 mapping
    xpath_queries = [
        "//*[local-name()='F15_2014']/*[local-name()='PROCEDURE']/*[local-name()='DIRECTIVE_2014_24_EU']/*[local-name()='PT_NEGOTIATED_WITHOUT_PUBLICATION']/*[local-name()='D_JUSTIFICATION']/text()",
        "//*[local-name()='F15_2014']/*[local-name()='PROCEDURE']/*[local-name()='DIRECTIVE_2014_25_EU']/*[local-name()='PT_NEGOTIATED_WITHOUT_PUBLICATION']/*[local-name()='D_JUSTIFICATION']/text()",
        "//*[local-name()='F15_2014']/*[local-name()='PROCEDURE']/*[local-name()='DIRECTIVE_2014_23_EU']/*[local-name()='PT_AWARD_CONTRACT_WITHOUT_PUBLICATION']/*[local-name()='D_JUSTIFICATION']/text()",
        "//*[local-name()='F21_2014']/*[local-name()='PROCEDURE']/*[local-name()='PT_AWARD_CONTRACT_WITHOUT_CALL']/*[local-name()='D_JUSTIFICATION']/text()",
        "//*[local-name()='F22_2014']/*[local-name()='PROCEDURE']/*[local-name()='PT_AWARD_CONTRACT_WITHOUT_CALL']/*[local-name()='D_JUSTIFICATION']/text()",
        "//*[local-name()='F23_2014']/*[local-name()='PROCEDURE']/*[local-name()='PT_AWARD_CONTRACT_WITHOUT_PUBLICATION']/*[local-name()='D_JUSTIFICATION']/text()",
        "//*[local-name()='F25_2014']/*[local-name()='PROCEDURE']/*[local-name()='PT_AWARD_CONTRACT_WITHOUT_PUBLICATION']/*[local-name()='D_JUSTIFICATION']/text()",
    ]

    for xpath_query in xpath_queries:
        justifications = root.xpath(xpath_query)
        # Filter out empty strings and join multiple paragraphs if present
        texts = [j.strip() for j in justifications if j and j.strip()]
        if texts:
            rationale = " ".join(texts)
            return {"tender": {"procurementMethodRationale": rationale}}

    return None


def merge_direct_award_justification_rationale(
    release_json: dict, direct_award_data: dict | None
) -> None:
    """Merge direct award justification data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        direct_award_data (Optional[Dict]): The source data containing direct award justification
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.procurementMethodRationale field.
    """
    if not direct_award_data:
        logger.debug("No direct award justification data to merge")
        return

    if (
        "tender" not in direct_award_data
        or "procurementMethodRationale" not in direct_award_data["tender"]
    ):
        logger.warning("Invalid direct award justification data structure")
        return

    release_json.setdefault("tender", {}).update(
        {
            "procurementMethodRationale": direct_award_data["tender"][
                "procurementMethodRationale"
            ]
        }
    )

    logger.info("Merged direct award justification data")
