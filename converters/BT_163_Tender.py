# converters/BT_163_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_concession_value_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"awards": []}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        value_description = lot_tender.xpath("efac:ConcessionRevenue/efbc:ValueDescription/text()", namespaces=namespaces)
        
        if tender_id and value_description:
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:LotTender/cbc:ID[@schemeName='tender'] = '{tender_id[0]}']", namespaces=namespaces)
            
            if lot_result:
                result_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
                lot_id = lot_result[0].xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
                
                if result_id and lot_id:
                    award = {
                        "id": result_id[0],
                        "relatedLots": [lot_id[0]],
                        "valueCalculationMethod": value_description[0]
                    }
                    result["awards"].append(award)

    return result if result["awards"] else None

def merge_concession_value_description(release_json, concession_value_description_data):
    if not concession_value_description_data:
        logger.warning("No concession value description data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])
    
    for new_award in concession_value_description_data["awards"]:
        existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_award["valueCalculationMethod"] = new_award["valueCalculationMethod"]
            existing_award.setdefault("relatedLots", []).extend(new_award["relatedLots"])
            existing_award["relatedLots"] = list(set(existing_award["relatedLots"]))  # Remove duplicates
        else:
            existing_awards.append(new_award)

    logger.info(f"Merged concession value description data for {len(concession_value_description_data['awards'])} awards")