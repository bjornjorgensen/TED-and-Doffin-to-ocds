# converters/BT_51.py
from lxml import etree

def parse_maximum_candidates_number(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        maximum_quantity = lot_element.xpath(
            "cac:TenderingProcess/cac:EconomicOperatorShortList/cbc:MaximumQuantity/text()",
            namespaces=namespaces
        )
        
        if maximum_quantity:
            lot = {
                "id": lot_id,
                "secondStage": {
                    "maximumCandidates": int(maximum_quantity[0])
                }
            }
            result["tender"]["lots"].append(lot)
    
    return result if result["tender"]["lots"] else None

def merge_maximum_candidates_number(release_json, maximum_candidates_data):
    if maximum_candidates_data and "tender" in maximum_candidates_data and "lots" in maximum_candidates_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in maximum_candidates_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_second_stage = existing_lot.setdefault("secondStage", {})
                existing_second_stage["maximumCandidates"] = new_lot["secondStage"]["maximumCandidates"]
            else:
                existing_lots.append(new_lot)
