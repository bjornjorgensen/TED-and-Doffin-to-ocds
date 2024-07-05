# converters/BT_1711_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_ranked(xml_content):
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
        ranked_indicator = lot_tender.xpath("efbc:TenderRankedIndicator/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        
        if ranked_indicator:
            result["bids"]["details"].append({
                "id": tender_id,
                "hasRank": ranked_indicator[0].lower() == 'true',
                "relatedLots": [lot_id]
            })

    return result if result["bids"]["details"] else None

def merge_tender_ranked(release_json, tender_ranked_data):
    if not tender_ranked_data:
        logger.warning("No Tender Ranked data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    
    for new_bid in tender_ranked_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid["hasRank"] = new_bid["hasRank"]
            existing_bid["relatedLots"] = new_bid["relatedLots"]
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Tender Ranked data for {len(tender_ranked_data['bids']['details'])} bids")