# converters/BT_52.py
from lxml import etree

def parse_successive_reduction_indicator(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}

    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        successive_reduction = lot_element.xpath("cac:TenderingProcess/cbc:CandidateReductionConstraintIndicator/text()", namespaces=namespaces)
        
        if successive_reduction:
            lot = {
                "id": lot_id,
                "secondStage": {
                    "successiveReduction": successive_reduction[0].lower() == 'true'
                }
            }
            result["tender"]["lots"].append(lot)

    return result if result["tender"]["lots"] else None

def merge_successive_reduction_indicator(release_json, successive_reduction_data):
    if successive_reduction_data and "tender" in successive_reduction_data and "lots" in successive_reduction_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in successive_reduction_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("secondStage", {})["successiveReduction"] = new_lot["secondStage"]["successiveReduction"]
            else:
                existing_lots.append(new_lot)
