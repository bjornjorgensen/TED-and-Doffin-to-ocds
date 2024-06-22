# converters/BT_27.py
from lxml import etree

def parse_estimated_value(xml_content):
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
        estimated_value = lot_element.xpath("cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount", namespaces=namespaces)
        if estimated_value:
            lot = {
                "id": lot_id,
                "value": {
                    "amount": float(estimated_value[0].text),
                    "currency": estimated_value[0].get("currencyID")
                }
            }
            result["tender"]["lots"].append(lot)
    
    # Parse Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup_element in lotgroup_elements:
        lotgroup_id = lotgroup_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        estimated_value = lotgroup_element.xpath("cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount", namespaces=namespaces)
        if estimated_value:
            lotgroup = {
                "id": lotgroup_id,
                "maximumValue": {
                    "amount": float(estimated_value[0].text),
                    "currency": estimated_value[0].get("currencyID")
                }
            }
            result["tender"]["lotGroups"].append(lotgroup)
    
    # Parse Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount", namespaces=namespaces)
    if part_element:
        result["tender"]["value"] = {
            "amount": float(part_element[0].text),
            "currency": part_element[0].get("currencyID")
        }
    
    # Parse Procedure
    procedure_element = root.xpath("/*/cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount", namespaces=namespaces)
    if procedure_element:
        result["tender"]["value"] = {
            "amount": float(procedure_element[0].text),
            "currency": procedure_element[0].get("currencyID")
        }
    
    return result if (result["tender"]["lots"] or result["tender"]["lotGroups"] or "value" in result["tender"]) else None

def merge_estimated_value(release_json, estimated_value_data):
    if estimated_value_data and "tender" in estimated_value_data:
        tender = release_json.setdefault("tender", {})
        
        # Merge lots
        if "lots" in estimated_value_data["tender"]:
            existing_lots = tender.setdefault("lots", [])
            for new_lot in estimated_value_data["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot["value"] = new_lot["value"]
                else:
                    existing_lots.append(new_lot)
        
        # Merge lot groups
        if "lotGroups" in estimated_value_data["tender"]:
            existing_lotgroups = tender.setdefault("lotGroups", [])
            for new_lotgroup in estimated_value_data["tender"]["lotGroups"]:
                existing_lotgroup = next((lotgroup for lotgroup in existing_lotgroups if lotgroup["id"] == new_lotgroup["id"]), None)
                if existing_lotgroup:
                    existing_lotgroup["maximumValue"] = new_lotgroup["maximumValue"]
                else:
                    existing_lotgroups.append(new_lotgroup)
        
        # Merge tender value (Part and Procedure)
        if "value" in estimated_value_data["tender"]:
            tender["value"] = estimated_value_data["tender"]["value"]
