# converters/BT_720_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_value(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1'
    }

    result = {"bids": {"details": []}, "awards": []}
    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)[0]
        amount = lot_tender.xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/text()", namespaces=namespaces)
        currency = lot_tender.xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/@currencyID", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]

        if amount and currency:
            bid = {
                "id": tender_id,
                "value": {
                    "amount": float(amount[0]),
                    "currency": currency[0]
                }
            }
            result["bids"]["details"].append(bid)

            # Find corresponding LotResult
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:LotTender/cbc:ID[@schemeName='tender']/text()='{tender_id}']", namespaces=namespaces)
            if lot_result:
                award_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0]
                award = {
                    "id": award_id,
                    "value": {
                        "amount": float(amount[0]),
                        "currency": currency[0]
                    },
                    "relatedLots": [lot_id]
                }
                result["awards"].append(award)

    return result if (result["bids"]["details"] or result["awards"]) else None

def merge_tender_value(release_json, tender_value_data):
    if not tender_value_data:
        logger.warning("No Tender Value data to merge")
        return

    if "bids" not in release_json:
        release_json["bids"] = {"details": []}
    if "awards" not in release_json:
        release_json["awards"] = []

    for new_bid in tender_value_data["bids"]["details"]:
        existing_bid = next((bid for bid in release_json["bids"]["details"] if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid["value"] = new_bid["value"]
        else:
            release_json["bids"]["details"].append(new_bid)

    for new_award in tender_value_data["awards"]:
        existing_award = next((award for award in release_json["awards"] if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_award["value"] = new_award["value"]
            existing_award["relatedLots"] = new_award["relatedLots"]
        else:
            release_json["awards"].append(new_award)

    logger.info(f"Merged Tender Value data for {len(tender_value_data['bids']['details'])} bids and {len(tender_value_data['awards'])} awards")