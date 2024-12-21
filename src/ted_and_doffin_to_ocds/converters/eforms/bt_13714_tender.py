# converters/bt_13714_Tender.py

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


def parse_tender_lot_identifier(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse tender lot identifier (BT-13714) from XML content.

    Gets tender and lot identifiers from each lot tender. Creates/updates
    corresponding Bid objects in bids.details array with related lots.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing bids with lot references or None if no data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"bids": {"details": []}}

        lot_tenders = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:LotTender",
            namespaces=NAMESPACES,
        )

        for lot_tender in lot_tenders:
            try:
                tender_id = lot_tender.xpath(
                    "cbc:ID[@schemeName='tender']/text()",
                    namespaces=NAMESPACES,
                )[0]

                lot_id = lot_tender.xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=NAMESPACES,
                )[0]

                if tender_id and lot_id:
                    result["bids"]["details"].append(
                        {"id": tender_id, "relatedLots": [lot_id]}
                    )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot tender data: %s", e)
                continue

        if result["bids"]["details"]:
            return result

    except Exception:
        logger.exception("Error parsing tender lot identifiers")
        return None

    return None


def merge_tender_lot_identifier(
    release_json: dict[str, Any], tender_lot_data: dict[str, Any] | None
) -> None:
    """Merge tender lot identifiers into the release JSON.

    Updates or creates bids with lot references.
    Preserves existing bid data while adding/updating related lots.

    Args:
        release_json: The target release JSON to update
        tender_lot_data: The source data containing lot tenders to merge

    Returns:
        None

    """
    if not tender_lot_data:
        logger.warning("No Tender Lot Identifier data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])

    for new_bid in tender_lot_data["bids"]["details"]:
        existing_bid = next(
            (bid for bid in existing_bids if bid["id"] == new_bid["id"]),
            None,
        )
        if existing_bid:
            existing_bid.setdefault("relatedLots", []).extend(
                lot
                for lot in new_bid["relatedLots"]
                if lot not in existing_bid["relatedLots"]
            )
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged Tender Lot Identifier data for %d bids",
        len(tender_lot_data["bids"]["details"]),
    )
