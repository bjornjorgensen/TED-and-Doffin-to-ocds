import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-142: Winner Chosen
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT/*[matches(name(),'AWARDED_CONTRACT')]
# - TED_EXPORT/FORM_SECTION/F13_2014/RESULTS/*[matches(name(),'AWARDED_PRIZE')]
# - TED_EXPORT/FORM_SECTION/F21_2014/AWARD_CONTRACT/*[matches(name(),'AWARDED_CONTRACT')]
# - TED_EXPORT/FORM_SECTION/F22_2014/AWARD_CONTRACT/*[matches(name(),'AWARDED_CONTRACT')]
# - TED_EXPORT/FORM_SECTION/F25_2014/AWARD_CONTRACT/*[matches(name(),'AWARDED_CONTRACT')]
# OCDS Mapping: awards[].status, awards[].statusDetails, awards[].relatedLots, tender.lots[].status

# Status code mapping based on authority table
STATUS_CODE_MAPPING = {
    "clos-nw": "No winner was chosen and the competition is closed.",
    "open-nw": "The winner was not yet chosen, but the competition is still ongoing.",
    "selec-w": "At least one winner was chosen.",
}


def parse_winner_chosen(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the winner chosen status from TED XML.

    Args:
        xml_content: The TED XML content as string or bytes.

    Returns:
        A dictionary containing award and lot information, or None if no data found
        The structure follows:
        {
            "awards": [
                {
                    "id": str,
                    "status": str,
                    "statusDetails": str,
                    "relatedLots": [str]
                }
            ],
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "status": str
                    }
                ]
            }
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)

        result = {"awards": [], "tender": {"lots": []}}

        # Check for F03_2014 form (most common award form)
        award_contracts = root.xpath(
            "FORM_SECTION/F03_2014/AWARD_CONTRACT/*[contains(name(),'AWARDED_CONTRACT')]"
        )

        # Look for F13_2014 (prize results)
        if not award_contracts:
            award_contracts = root.xpath(
                "FORM_SECTION/F13_2014/RESULTS/*[contains(name(),'AWARDED_PRIZE')]"
            )

        # Check other forms (F21, F22, F25)
        if not award_contracts:
            for form in ["F21_2014", "F22_2014", "F25_2014"]:
                award_contracts = root.xpath(
                    f"FORM_SECTION/{form}/AWARD_CONTRACT/*[contains(name(),'AWARDED_CONTRACT')]"
                )
                if award_contracts:
                    break

        # Process found contracts
        for i, contract in enumerate(award_contracts):
            # Determine if contract was awarded
            awarded = contract.xpath("AWARDED_CONTRACT/text()")
            lot_id = contract.xpath("LOT_NO/text()")

            if lot_id and awarded:
                lot_id = lot_id[0].strip()
                awarded = awarded[0].strip()

                # Generate a result ID
                result_id = f"RES-{i + 1:04d}"

                # Map TED awarded values to eForms status codes
                if awarded.lower() == "yes":
                    # Equivalent to "selec-w"
                    status_code = "selec-w"
                    award = {
                        "id": result_id,
                        "status": "active",
                        "statusDetails": STATUS_CODE_MAPPING.get(
                            status_code, "At least one winner was chosen."
                        ),
                        "relatedLots": [lot_id],
                    }
                    result["awards"].append(award)
                elif awarded.lower() == "no":
                    # Check if it's "no award" (clos-nw) or "procurement still ongoing" (open-nw)
                    no_awarded_justification = contract.xpath(
                        "NO_AWARDED_CONTRACT/text()"
                    )

                    if (
                        no_awarded_justification
                        and "ongoing" in no_awarded_justification[0].lower()
                    ):
                        # Equivalent to "open-nw"
                        result["tender"]["lots"].append(
                            {"id": lot_id, "status": "active"}
                        )
                    else:
                        # Equivalent to "clos-nw"
                        status_code = "clos-nw"
                        award = {
                            "id": result_id,
                            "status": "unsuccessful",
                            "statusDetails": STATUS_CODE_MAPPING.get(
                                status_code,
                                "No winner was chosen and the competition is closed.",
                            ),
                            "relatedLots": [lot_id],
                        }
                        result["awards"].append(award)

        return result if (result["awards"] or result["tender"]["lots"]) else None

    except Exception as e:
        logger.warning("Error parsing winner chosen status: %s", e)

    return None


def merge_winner_chosen(
    release_json: dict[str, Any], parsed_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed winner chosen data into the release JSON.

    Args:
        release_json: The release JSON to merge into.
        parsed_data: The parsed data from parse_winner_chosen.
    """
    if not parsed_data:
        logger.info("No winner chosen data to merge.")
        return

    # Handle awards
    if parsed_data.get("awards"):
        existing_awards = release_json.setdefault("awards", [])

        for new_award in parsed_data["awards"]:
            # Try to find existing award with the same ID
            existing_award = next(
                (a for a in existing_awards if a.get("id") == new_award["id"]), None
            )

            if existing_award:
                # Update existing award
                existing_award.update(new_award)
            else:
                # Add new award
                existing_awards.append(new_award)

    # Handle lots
    if parsed_data.get("tender", {}).get("lots"):
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])

        for new_lot in parsed_data["tender"]["lots"]:
            # Try to find existing lot with the same ID
            existing_lot = next(
                (lot for lot in existing_lots if lot.get("id") == new_lot["id"]), None
            )

            if existing_lot:
                # Update existing lot
                existing_lot.update(new_lot)
            else:
                # Add new lot
                existing_lots.append(new_lot)

    awards_count = len(parsed_data.get("awards", []))
    lots_count = len(parsed_data.get("tender", {}).get("lots", []))

    logger.info(
        "Merged winner chosen data for %d awards and %d lots", awards_count, lots_count
    )
