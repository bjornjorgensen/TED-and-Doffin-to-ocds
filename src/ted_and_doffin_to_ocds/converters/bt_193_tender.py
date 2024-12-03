# converters/bt_193_Tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_variant(xml_content: str | bytes) -> dict | None:
    """
    Parse tender variant information from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing tender information

    Returns:
        Optional[Dict]: Dictionary containing bid information, or None if no data found
        The structure follows the format:
        {
            "bids": {
                "details": [
                    {
                        "id": str,
                        "variant": bool,
                        "relatedLots": [str]
                    }
                ]
            }
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        variant = lot_tender.xpath(
            "efbc:TenderVariantIndicator/text()",
            namespaces=namespaces,
        )
        lot_id = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if tender_id and lot_id:
            bid_data = {"id": tender_id[0], "relatedLots": [lot_id[0]]}

            if variant:
                bid_data["variant"] = variant[0].lower() == "true"

            result["bids"]["details"].append(bid_data)

    return result if result["bids"]["details"] else None


def merge_tender_variant(release_json: dict, tender_variant_data: dict | None) -> None:
    """
    Merge tender variant data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        tender_variant_data (Optional[Dict]): The source data containing bids
            to be merged. If None, function returns without making changes.
    """
    if not tender_variant_data:
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    for new_bid in tender_variant_data["bids"]["details"]:
        existing_bid = next(
            (b for b in existing_bids if b["id"] == new_bid["id"]),
            None,
        )
        if existing_bid:
            existing_bid.update(new_bid)
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged Tender Variant data for %d bids",
        len(tender_variant_data["bids"]["details"]),
    )
