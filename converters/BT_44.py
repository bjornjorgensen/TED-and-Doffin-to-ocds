# converters/BT_44.py
from lxml import etree

def parse_prize_rank(xml_content):
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
                rank_code = prize_element.xpath("cbc:RankCode/text()", namespaces=namespaces)
                if rank_code:
                    prizes.append({
                        "id": str(index),
                        "rank": int(rank_code[0])
                    })
            
            # Sort prizes by rank
            prizes.sort(key=lambda x: x["rank"])
            
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

def merge_prize_rank(release_json, prize_rank_data):
    if prize_rank_data and "tender" in prize_rank_data and "lots" in prize_rank_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in prize_rank_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_design_contest = existing_lot.setdefault("designContest", {})
                existing_prizes = existing_design_contest.setdefault("prizes", {}).setdefault("details", [])
                
                for new_prize in new_lot["designContest"]["prizes"]["details"]:
                    existing_prize = next((prize for prize in existing_prizes if prize["id"] == new_prize["id"]), None)
                    if existing_prize:
                        existing_prize.update(new_prize)
                    else:
                        existing_prizes.append(new_prize)
                
                # Sort prizes by rank
                existing_prizes.sort(key=lambda x: x.get("rank", float('inf')))
            else:
                existing_lots.append(new_lot)
