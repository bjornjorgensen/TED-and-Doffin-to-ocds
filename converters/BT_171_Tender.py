# converters/BT_171_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_rank(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        rank_code = lot_tender.xpath("cbc:RankCode/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)

        if tender_id:
            bid = {
                "id": tender_id[0],
                "relatedLots": [lot_id[0]] if lot_id else []
            }
            if rank_code:
                bid["rank"] = int(rank_code[0])

            result["bids"]["details"].append(bid)

    return result if result["bids"]["details"] else None

def merge_tender_rank(release_json, tender_rank_data):
    if not tender_rank_data:
        logger.warning("No Tender Rank data to merge")
        return

    existing_bids = {bid.get("id"): bid for bid in release_json.get("bids", {}).get("details", [])}
    for bid in tender_rank_data["bids"]["details"]:
        if bid["id"] in existing_bids:
            existing_bids[bid["id"]].update(bid)
        else:
            release_json.setdefault("bids", {}).setdefault("details", []).append(bid)

    logger.info(f"Merged Tender Rank data for {len(tender_rank_data['bids']['details'])} bids")