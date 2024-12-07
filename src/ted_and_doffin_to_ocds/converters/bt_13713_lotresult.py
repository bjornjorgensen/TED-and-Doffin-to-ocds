# converters/bt_13713_LotResult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_lot_result_identifier(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse lot result identifier (BT-13713) from XML content.

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

        lot_results = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:LotResult",
            namespaces=NAMESPACES,
        )

        for lot_result in lot_results:
            try:
                award_id = lot_result.xpath(
                    "cbc:ID[@schemeName='result']/text()", namespaces=NAMESPACES
                )[0]

                lot_id = lot_result.xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=NAMESPACES,
                )[0]

                if award_id and lot_id:
                    result["awards"].append({"id": award_id, "relatedLots": [lot_id]})

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
    """
    Merge lot result identifiers into the release JSON.

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
