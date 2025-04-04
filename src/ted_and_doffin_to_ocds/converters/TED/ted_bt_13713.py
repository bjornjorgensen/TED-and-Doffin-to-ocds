import logging
import re
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# Pattern for valid lot IDs as per specification
LOT_ID_PATTERN = re.compile(r"^LOT-\d{4}$")


def parse_lot_result_identifier(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse lot result identifier (BT-13713) from TED XML content.

    Gets award and lot identifiers from each award contract section. Creates/updates
    corresponding Award objects in awards array with related lots.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing awards with lot references or None if no data found

    Note:
        According to TED guidance, if a lot number isn't specified, it defaults to '1'.
        The lot ID must follow the pattern ^LOT-\\d{4}$ (LOT- followed by exactly 4 digits).
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"awards": []}

        # TED XML doesn't use namespaces in the same way as eForms
        # XPaths for lot numbers in award contract sections based on different form types
        lot_paths = [
            "//TED_EXPORT/FORM_SECTION/F03_2014/AWARD_CONTRACT",
            "//TED_EXPORT/FORM_SECTION/F15_2014/AWARD_CONTRACT",
            "//TED_EXPORT/FORM_SECTION/F20_2014/AWARD_CONTRACT",
            "//TED_EXPORT/FORM_SECTION/F21_2014/AWARD_CONTRACT",
            "//TED_EXPORT/FORM_SECTION/F22_2014/AWARD_CONTRACT",
            "//TED_EXPORT/FORM_SECTION/F23_2014/AWARD_CONTRACT",
            "//TED_EXPORT/FORM_SECTION/F25_2014/AWARD_CONTRACT",
        ]

        award_counter = 1

        for base_path in lot_paths:
            award_contracts = root.xpath(base_path)

            for award_contract in award_contracts:
                try:
                    # Extract lot number
                    lot_nodes = award_contract.xpath("./LOT_NO")

                    # If no lot number is set, default to '1' as per TED guidance
                    if (
                        not lot_nodes
                        or not lot_nodes[0].text
                        or not lot_nodes[0].text.strip()
                    ):
                        lot_number = "1"
                    else:
                        lot_number = lot_nodes[0].text.strip()

                    # Format the lot ID to match required pattern LOT-XXXX
                    try:
                        lot_id = f"LOT-{int(lot_number):04d}"
                    except ValueError:
                        logger.warning(
                            "Invalid lot number '%s', using default LOT-0001",
                            lot_number,
                        )
                        lot_id = "LOT-0001"

                    # Generate a unique award ID if none exists
                    award_id = f"RES-{award_counter:04d}"
                    award_counter += 1

                    result["awards"].append({"id": award_id, "relatedLots": [lot_id]})
                    logger.debug("Found award %s related to lot %s", award_id, lot_id)

                except Exception as e:
                    logger.warning("Error processing award contract: %s", e)
                    continue

        if result["awards"]:
            return result

    except Exception:
        logger.exception("Error parsing lot result identifiers")
        return None

    return None


def merge_lot_result_identifier(
    release_json: dict[str, Any], lot_result_data: dict[str, Any] | None
) -> None:
    """Merge lot result identifiers into the release JSON.

    Updates or creates awards with lot references.
    Preserves existing award data while adding/updating related lots.

    Args:
        release_json: The target release JSON to update
        lot_result_data: The source data containing lot results to merge

    Returns:
        None
    """
    if not lot_result_data:
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in lot_result_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )

        if existing_award:
            existing_lots = set(existing_award.get("relatedLots", []))
            existing_lots.update(new_award["relatedLots"])
            existing_award["relatedLots"] = list(existing_lots)
            logger.info("Updated relatedLots for award %s", new_award["id"])
        else:
            existing_awards.append(new_award)
            logger.info("Added new award with id: %s", new_award["id"])
