# converters/BT_46.py
from lxml import etree

def parse_jury_member_name(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        jury_member_elements = lot_element.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cac:TechnicalCommitteePerson/cbc:FamilyName",
            namespaces=namespaces
        )
        
        if jury_member_elements:
            jury_members = [{"name": member.text} for member in jury_member_elements]
            
            lot = {
                "id": lot_id,
                "designContest": {
                    "juryMembers": jury_members
                }
            }
            result["tender"]["lots"].append(lot)
    
    return result if result["tender"]["lots"] else None

def merge_jury_member_name(release_json, jury_member_name_data):
    if jury_member_name_data and "tender" in jury_member_name_data and "lots" in jury_member_name_data["tender"]:
        tender = release_json.setdefault("tender", {})
        existing_lots = tender.setdefault("lots", [])
        
        for new_lot in jury_member_name_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_design_contest = existing_lot.setdefault("designContest", {})
                existing_jury_members = existing_design_contest.setdefault("juryMembers", [])
                
                for new_jury_member in new_lot["designContest"]["juryMembers"]:
                    if new_jury_member not in existing_jury_members:
                        existing_jury_members.append(new_jury_member)
            else:
                existing_lots.append(new_lot)
