# converters/BT_50_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_minimum_candidates(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        minimum_quantity = lot_element.xpath(".//cac:EconomicOperatorShortList/cbc:MinimumQuantity/text()", namespaces=namespaces)
        
        if minimum_quantity:
            lot = {
                "id": lot_id,
                "secondStage": {
                    "minimumCandidates": int(minimum_quantity[0])
                }
            }
            result["tender"]["lots"].append(lot)

    return result if result["tender"]["lots"] else None

def merge_minimum_candidates(release_json, minimum_candidates_data):
    if not minimum_candidates_data:
        logger.warning("No Minimum Candidates data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in minimum_candidates_data["tender"]["lots"]:
        existing_lot = next((lot for lot in tender_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("secondStage", {}).update(new_lot["secondStage"])
        else:
            tender_lots.append(new_lot)

    logger.info(f"Merged Minimum Candidates data for {len(minimum_candidates_data['tender']['lots'])} lots")