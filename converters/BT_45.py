# converters/BT_45.py
from lxml import etree

def parse_rewards_other(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        prize_elements = lot_element.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cac:Prize",
            namespaces=namespaces
        )
        
        if prize_elements:
            prizes = []
            for index, prize_element in enumerate(prize_elements):
                description = prize_element.xpath("cbc:Description/text()", namespaces=namespaces)
                if description:
                    prizes.append({
                        "id": str(index),
                        "description": description[0]
                    })
            
            lot = {
                "id": lot_id,
                "designContest": {
                    "prizes": {
                        "details": prizes
                    }
                }
            }
            result["tender"]["lots"].append(lot)
    
    return result if result["tender"]["lots"] else None

def merge_rewards_other(release_json, rewards_other_data):
    if rewards_other_data and "tender" in rewards_other_data and "lots" in rewards_other_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in rewards_other_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_design_contest = existing_lot.setdefault("designContest", {})
                existing_prizes = existing_design_contest.setdefault("prizes", {}).setdefault("details", [])
                
                for new_prize in new_lot["designContest"]["prizes"]["details"]:
                    existing_prize = next((prize for prize in existing_prizes if prize["id"] == new_prize["id"]), None)
                    if existing_prize:
                        existing_prize["description"] = new_prize["description"]
                    else:
                        existing_prizes.append(new_prize)
            else:
                existing_lots.append(new_lot)
