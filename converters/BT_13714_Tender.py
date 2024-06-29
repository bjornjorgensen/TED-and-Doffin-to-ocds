# converters/BT_13714_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"bids": {"details": []}}
    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        bid_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)

        if bid_id and lot_id:
            bid = next((b for b in result["bids"]["details"] if b["id"] == bid_id[0]), None)
            if not bid:
                bid = {"id": bid_id[0], "relatedLots": []}
                result["bids"]["details"].append(bid)
            
            if lot_id[0] not in bid["relatedLots"]:
                bid["relatedLots"].append(lot_id[0])

    return result if result["bids"]["details"] else None

def merge_tender_lot_identifier(release_json, tender_lot_data):
    if not tender_lot_data:
        logger.warning("No Tender Lot Identifier data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    
    for new_bid in tender_lot_data["bids"]["details"]:
        existing_bid = next((b for b in existing_bids if b["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid.setdefault("relatedLots", []).extend(
                lot for lot in new_bid["relatedLots"] if lot not in existing_bid.get("relatedLots", [])
            )
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Tender Lot Identifier data for {len(tender_lot_data['bids']['details'])} bids")