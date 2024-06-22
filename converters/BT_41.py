# converters/BT_41.py
from lxml import etree

def parse_following_contract(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        followup_contract_indicator = lot_element.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cbc:FollowupContractIndicator/text()",
            namespaces=namespaces
        )
        
        if followup_contract_indicator:
            lot = {
                "id": lot_id,
                "designContest": {
                    "followUpContracts": followup_contract_indicator[0].lower() == "true"
                }
            }
            result["tender"]["lots"].append(lot)
    
    return result if result["tender"]["lots"] else None

def merge_following_contract(release_json, following_contract_data):
    if following_contract_data and "tender" in following_contract_data and "lots" in following_contract_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in following_contract_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("designContest", {})["followUpContracts"] = new_lot["designContest"]["followUpContracts"]
            else:
                existing_lots.append(new_lot)
