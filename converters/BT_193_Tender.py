# converters/BT_193_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_variant(xml_content):
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
        "//efac:NoticeResult/efac:LotTender", namespaces=namespaces
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )[0]
        variant_indicator = lot_tender.xpath(
            "efbc:TenderVariantIndicator/text()", namespaces=namespaces
        )
        lot_id = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces
        )[0]

        bid = {"id": tender_id, "relatedLots": [lot_id]}

        if variant_indicator:
            bid["variant"] = variant_indicator[0].lower() == "true"

        result["bids"]["details"].append(bid)

    return result if result["bids"]["details"] else None


def merge_tender_variant(release_json, tender_variant_data):
    if not tender_variant_data:
        logger.warning("No Tender Variant data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])

    for new_bid in tender_variant_data["bids"]["details"]:
        existing_bid = next(
            (bid for bid in existing_bids if bid["id"] == new_bid["id"]), None
        )
        if existing_bid:
            existing_bid.update(new_bid)
        else:
            existing_bids.append(new_bid)

    logger.info(
        f"Merged Tender Variant data for {len(tender_variant_data['bids']['details'])} bids"
    )
