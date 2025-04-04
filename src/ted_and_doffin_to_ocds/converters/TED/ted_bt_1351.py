import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_accelerated_procedure_justification(xml_content: str | bytes) -> dict | None:
    """Parse the accelerated procedure justification text (BT-1351) from TED XML content.

    Maps to tender.procedure.acceleratedRationale in OCDS.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse

    Returns:
        Optional[Dict]: Dictionary containing accelerated procedure rationale, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "procedure": {
                    "acceleratedRationale": str
                }
            }
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    # Try to extract accelerated procedure justification from multiple TED form types based on BT-1351 mapping
    xpath_queries = [
        "//*[local-name()='F02_2014']/*[local-name()='PROCEDURE']/*[local-name()='ACCELERATED_PROC']/*[local-name()='P']/text()",
        "//*[local-name()='F03_2014']/*[local-name()='PROCEDURE']/*[local-name()='ACCELERATED_PROC']/*[local-name()='P']/text()",
        "//*[local-name()='CONTRACT_DEFENCE']/*[local-name()='FD_CONTRACT_DEFENCE']/*[local-name()='PROCEDURE_DEFINITION_CONTRACT_NOTICE_DEFENCE']/*[local-name()='TYPE_OF_PROCEDURE_DEFENCE']/*[local-name()='TYPE_OF_PROCEDURE_DETAIL_FOR_CONTRACT_NOTICE_DEFENCE']/*[local-name()='PT_ACCELERATED_RESTRICTED_CHOICE']/*[local-name()='PTAR_JUSTIFICATION']/text()",
        "//*[local-name()='CONTRACT_DEFENCE']/*[local-name()='FD_CONTRACT_DEFENCE']/*[local-name()='PROCEDURE_DEFINITION_CONTRACT_NOTICE_DEFENCE']/*[local-name()='TYPE_OF_PROCEDURE_DEFENCE']/*[local-name()='TYPE_OF_PROCEDURE_DETAIL_FOR_CONTRACT_NOTICE_DEFENCE']/*[local-name()='F17_PT_ACCELERATED_NEGOTIATED']/*[local-name()='PTAN_JUSTIFICATION']/text()",
    ]

    for xpath_query in xpath_queries:
        justifications = root.xpath(xpath_query)
        # Filter out empty strings and join multiple paragraphs if present
        texts = [j.strip() for j in justifications if j and j.strip()]
        if texts:
            rationale = " ".join(texts)
            return {"tender": {"procedure": {"acceleratedRationale": rationale}}}

    logger.info("No accelerated procedure justification found in TED XML")
    return None


def merge_accelerated_procedure_justification(
    release_json: dict, accelerated_data: dict | None
) -> None:
    """Merge accelerated procedure justification data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        accelerated_data (Optional[Dict]): The source data containing accelerated procedure justification
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.procedure.acceleratedRationale field.
    """
    if not accelerated_data:
        logger.debug("No accelerated procedure justification data to merge")
        return

    if (
        "tender" not in accelerated_data
        or "procedure" not in accelerated_data["tender"]
        or "acceleratedRationale" not in accelerated_data["tender"]["procedure"]
    ):
        logger.warning("Invalid accelerated procedure justification data structure")
        return

    tender = release_json.setdefault("tender", {})
    procedure = tender.setdefault("procedure", {})
    procedure["acceleratedRationale"] = accelerated_data["tender"]["procedure"][
        "acceleratedRationale"
    ]

    logger.info("Merged accelerated procedure justification data")
