# converters/BT_300.py
from lxml import etree

def parse_additional_information(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": [], "lotGroups": []}}
    
    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        additional_info = lot_element.xpath("cac:ProcurementProject/cbc:Note/text()", namespaces=namespaces)
        if additional_info:
            lot = {
                "id": lot_id,
                "description": " ".join(additional_info)
            }
            result["tender"]["lots"].append(lot)
    
    # Parse Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup_element in lotgroup_elements:
        lotgroup_id = lotgroup_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        additional_info = lotgroup_element.xpath("cac:ProcurementProject/cbc:Note/text()", namespaces=namespaces)
        if additional_info:
            lotgroup = {
                "id": lotgroup_id,
                "description": " ".join(additional_info)
            }
            result["tender"]["lotGroups"].append(lotgroup)
    
    # Parse Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Note/text()", namespaces=namespaces)
    if part_element:
        result["description"] = " ".join(part_element)
    
    # Parse Procedure
    procedure_element = root.xpath("/*/cac:ProcurementProject/cbc:Note/text()", namespaces=namespaces)
    if procedure_element:
        result["description"] = " ".join(procedure_element)
    
    return result if (result["tender"]["lots"] or result["tender"]["lotGroups"] or "description" in result) else None

def merge_additional_information(release_json, additional_info_data):
    if additional_info_data:
        # Merge lots
        if "tender" in additional_info_data and "lots" in additional_info_data["tender"]:
            existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
            for new_lot in additional_info_data["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot["description"] = existing_lot.get("description", "") + " " + new_lot["description"]
                else:
                    existing_lots.append(new_lot)
        
        # Merge lot groups
        if "tender" in additional_info_data and "lotGroups" in additional_info_data["tender"]:
            existing_lotgroups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
            for new_lotgroup in additional_info_data["tender"]["lotGroups"]:
                existing_lotgroup = next((lotgroup for lotgroup in existing_lotgroups if lotgroup["id"] == new_lotgroup["id"]), None)
                if existing_lotgroup:
                    existing_lotgroup["description"] = existing_lotgroup.get("description", "") + " " + new_lotgroup["description"]
                else:
                    existing_lotgroups.append(new_lotgroup)
        
        # Merge description (Part and Procedure)
        if "description" in additional_info_data:
            release_json["description"] = release_json.get("description", "") + " " + additional_info_data["description"]
