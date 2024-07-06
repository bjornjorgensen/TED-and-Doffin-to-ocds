import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_tender_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id_elements = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        lot_id_elements = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if not tender_id_elements:
            logger.warning("Tender ID is missing for a LotTender")
            continue
        if not lot_id_elements:
            logger.warning("Lot ID is missing for a LotTender")
            continue
        
        tender_id = tender_id_elements[0]
        lot_id = lot_id_elements[0]
        
        existing_bid = next((bid for bid in result["bids"]["details"] if bid["id"] == tender_id), None)
        if existing_bid:
            if lot_id not in existing_bid["relatedLots"]:
                existing_bid["relatedLots"].append(lot_id)
        else:
            result["bids"]["details"].append({
                "id": tender_id,
                "relatedLots": [lot_id]
            })

    return result

def merge_tender_lot_identifier(release_json, tender_lot_identifier_data):
    if not tender_lot_identifier_data:
        logger.warning("No Tender Lot Identifier data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    
    for new_bid in tender_lot_identifier_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid.setdefault("relatedLots", [])
            for lot_id in new_bid["relatedLots"]:
                if lot_id not in existing_bid["relatedLots"]:
                    existing_bid["relatedLots"].append(lot_id)
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Tender Lot Identifier data for {len(tender_lot_identifier_data['bids']['details'])} bids")