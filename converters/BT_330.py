# converters/BT_330.py
from lxml import etree

def parse_procedure_group_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lotGroups": []}}
    
    # Parse Procedure Group Identifier
    lots_group_elements = root.xpath("/*/cac:TenderingTerms/cac:LotDistribution/cac:LotsGroup/cbc:LotsGroupID", namespaces=namespaces)
    for lots_group_element in lots_group_elements:
        group_id = lots_group_element.text
        result["tender"]["lotGroups"].append({"id": group_id})
    
    return result if result["tender"]["lotGroups"] else None

def merge_procedure_group_identifier(release_json, procedure_group_identifier_data):
    if procedure_group_identifier_data and "tender" in procedure_group_identifier_data and "lotGroups" in procedure_group_identifier_data["tender"]:
        existing_lot_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
        existing_group_ids = {group["id"] for group in existing_lot_groups}
        
        for new_group in procedure_group_identifier_data["tender"]["lotGroups"]:
            if new_group["id"] not in existing_group_ids:
                existing_lot_groups.append(new_group)
                existing_group_ids.add(new_group["id"])
