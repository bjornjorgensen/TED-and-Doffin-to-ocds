# converters/BT_42.py
from lxml import etree

def parse_jury_decision_binding(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        binding_on_buyer_indicator = lot_element.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cbc:BindingOnBuyerIndicator/text()",
            namespaces=namespaces
        )
        
        if binding_on_buyer_indicator:
            lot = {
                "id": lot_id,
                "designContest": {
                    "bindingJuryDecision": binding_on_buyer_indicator[0].lower() == "true"
                }
            }
            result["tender"]["lots"].append(lot)
    
    return result if result["tender"]["lots"] else None

def merge_jury_decision_binding(release_json, jury_decision_binding_data):
    if jury_decision_binding_data and "tender" in jury_decision_binding_data and "lots" in jury_decision_binding_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in jury_decision_binding_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("designContest", {})["bindingJuryDecision"] = new_lot["designContest"]["bindingJuryDecision"]
            else:
                existing_lots.append(new_lot)
