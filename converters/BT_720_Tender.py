from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_value(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"bids": {"details": []}, "awards": []}
    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)[0]
        amount = lot_tender.xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/text()", namespaces=namespaces)
        currency = lot_tender.xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/@currencyID", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)

        bid = {
            "id": tender_id,
            "relatedLots": lot_id
        }

        if amount and currency:
            bid["value"] = {
                "amount": float(amount[0]),
                "currency": currency[0]
            }

        result["bids"]["details"].append(bid)

        # Find corresponding LotResult and create Award
        lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:LotTender/cbc:ID[@schemeName='tender']/text()='{tender_id}']", namespaces=namespaces)
        if lot_result:
            result_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0]
            award = {
                "id": result_id,
                "relatedLots": lot_id
            }
            if amount and currency:
                award["value"] = {
                    "amount": float(amount[0]),
                    "currency": currency[0]
                }
            result["awards"].append(award)

    return result

def merge_tender_value(release_json, tender_value_data):
    if not tender_value_data:
        logger.warning("No Tender Value data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    existing_awards = release_json.setdefault("awards", [])
    
    for new_bid in tender_value_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid.update(new_bid)
        else:
            existing_bids.append(new_bid)

    for new_award in tender_value_data["awards"]:
        existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_award.update(new_award)
        else:
            existing_awards.append(new_award)

    logger.info(f"Merged Tender Value data for {len(tender_value_data['bids']['details'])} bids and {len(tender_value_data['awards'])} awards")