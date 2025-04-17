import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)

# BT-1451: Winner Decision Date
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F13_2014/RESULTS/AWARDED_PRIZE/DATE_DECISION_JURY
# - TED_EXPORT/FORM_SECTION/F15_2014/AWARD_CONTRACT/AWARDED_CONTRACT/DATE_CONCLUSION_CONTRACT
# OCDS Mapping: awards[].date


def parse_winner_decision_date(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses the winner decision date from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing award dates,
        or None if no awards are found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"awards": []}

        # Check for F13_2014 form (design contest results)
        awarded_prizes = root.xpath("FORM_SECTION/F13_2014/RESULTS/AWARDED_PRIZE")

        for i, prize in enumerate(awarded_prizes):
            decision_date = prize.xpath("DATE_DECISION_JURY/text()")
            if not decision_date:
                continue

            decision_date = decision_date[0].strip()

            # Generate award ID (consistent with other converters)
            award_id = f"RES-{i + 1:04d}"

            award = {"id": award_id, "date": end_date(decision_date)}

            result["awards"].append(award)
            logger.info("Found award %s with decision date %s", award_id, decision_date)

        # Check for F15_2014 form (voluntary ex ante)
        award_contracts = root.xpath(
            "FORM_SECTION/F15_2014/AWARD_CONTRACT/AWARDED_CONTRACT"
        )

        for i, contract in enumerate(award_contracts):
            conclusion_date = contract.xpath("DATE_CONCLUSION_CONTRACT/text()")
            if not conclusion_date:
                continue

            conclusion_date = conclusion_date[0].strip()

            # Generate award ID (based on same pattern used in other converters)
            award_id = f"RES-{len(result['awards']) + i + 1:04d}"

            award = {"id": award_id, "date": end_date(conclusion_date)}

            result["awards"].append(award)
            logger.info(
                "Found award %s with decision date %s", award_id, conclusion_date
            )

        return result if result["awards"] else None

    except Exception:
        logger.exception("Error parsing winner decision date")
        return None


def merge_winner_decision_date(
    release_json: dict[str, Any],
    winner_decision_date_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the winner decision date data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        winner_decision_date_data (Optional[Dict[str, List[Dict[str, Any]]]]):
            The winner decision date data to merge.

    Returns:
        None
    """
    if not winner_decision_date_data:
        logger.info("No Winner Decision Date data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in winner_decision_date_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )

        if existing_award:
            if (
                "date" not in existing_award
                or new_award["date"] < existing_award["date"]
            ):
                existing_award["date"] = new_award["date"]
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged Winner Decision Date data for %d awards",
        len(winner_decision_date_data["awards"]),
    )
