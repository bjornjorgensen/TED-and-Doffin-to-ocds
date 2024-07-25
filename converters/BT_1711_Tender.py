# converters/BT_1711_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_tender_ranked(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        ranked_indicator = lot_tender.xpath("efbc:TenderRankedIndicator/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if tender_id and ranked_indicator and lot_id:
            bid = {
                "id": tender_id[0],
                "hasRank": ranked_indicator[0].lower() == 'true',
                "relatedLots": [lot_id[0]]
            }
            result["bids"]["details"].append(bid)

    return result if result["bids"]["details"] else None

def merge_tender_ranked(release_json, tender_ranked_data):
    if not tender_ranked_data:
        logger.warning("No Tender Ranked data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    
    for new_bid in tender_ranked_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid.update(new_bid)
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Tender Ranked data for {len(tender_ranked_data['bids']['details'])} bids")