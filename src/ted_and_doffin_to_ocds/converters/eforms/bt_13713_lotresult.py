# converters/bt_13713_LotResult.py

import logging
import re
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

# Pattern for valid lot IDs as per specification
LOT_ID_PATTERN = re.compile(r"^LOT-\d{4}$")


def parse_lot_result_identifier(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse lot result identifier (BT-13713) from XML content.

    Gets award and lot identifiers from each lot result. Creates/updates
    corresponding Award objects in awards array with related lots.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing awards with lot references or None if no data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"awards": []}

        # Modified to check both uppercase and lowercase versions of NoticeResult
        lot_results = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:LotResult | "
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:noticeResult/efac:LotResult",
            namespaces=NAMESPACES,
        )

        for lot_result in lot_results:
            try:
                award_id = lot_result.xpath(
                    "cbc:ID[@schemeName='result']/text()", namespaces=NAMESPACES
                )

                # Properly handle missing award ID
                if not award_id:
                    logger.warning("Missing award ID in lot result, skipping")
                    continue
                award_id = award_id[0]

                # Skip if award_id is None or empty string
                if not award_id or award_id.lower() == "none":
                    logger.warning("Invalid award ID in lot result, skipping")
                    continue

                lot_ids = lot_result.xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=NAMESPACES,
                )

                # If no lot ID is set, set it to '1' as per TED guidance
                if not lot_ids:
                    lot_id = "LOT-0001"
                    logger.info("No lot ID found, using default: %s", lot_id)
                else:
                    lot_id = lot_ids[0]

                # Validate the lot ID pattern
                if not LOT_ID_PATTERN.match(lot_id):
                    logger.warning(
                        "Lot ID %s does not match required pattern ^LOT-\\d{4}$, it may be rejected",
                        lot_id,
                    )

                result["awards"].append({"id": award_id, "relatedLots": [lot_id]})
                logger.debug("Found award %s related to lot %s", award_id, lot_id)

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot result data: %s", e)
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
        logger.warning("No lot result identifier data to merge")
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
