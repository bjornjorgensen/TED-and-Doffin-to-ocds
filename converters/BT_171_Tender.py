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
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)[0]
        rank_code = lot_tender.xpath("cbc:RankCode/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        
        if rank_code:
            result["bids"]["details"].append({
                "id": tender_id,
                "rank": int(rank_code[0]),
                "relatedLots": [lot_id]
            })

    return result if result["bids"]["details"] else None

def merge_tender_rank(release_json, tender_rank_data):
    if not tender_rank_data:
        logger.warning("No Tender Rank data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    
    for new_bid in tender_rank_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid["rank"] = new_bid["rank"]
            if "relatedLots" not in existing_bid:
                existing_bid["relatedLots"] = new_bid["relatedLots"]
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Tender Rank data for {len(tender_rank_data['bids']['details'])} bids")