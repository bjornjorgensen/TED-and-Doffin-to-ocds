# converters/BT_24.py

from lxml import etree

def parse_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    # BT-24-Lot
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot.xpath("cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
        if description:
            result["tender"].setdefault("lots", []).append({
                "id": lot_id,
                "description": description[0]
            })

    # BT-24-LotsGroup
    lot_groups = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for group in lot_groups:
        group_id = group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = group.xpath("cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
        if description:
            result["tender"].setdefault("lotGroups", []).append({
                "id": group_id,
                "description": description[0]
            })

    # BT-24-Part
    part_description = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
    
    # BT-24-Procedure
    procedure_description = root.xpath("//cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)

    # Combine Part and Procedure description
    combined_description = part_description + procedure_description
    if combined_description:
        result["tender"]["description"] = combined_description[0]

    return result if result["tender"] else None

def merge_description(release_json, description_data):
    if not description_data:
        return

    tender = release_json.setdefault("tender", {})

    # Merge lots
    if "lots" in description_data["tender"]:
        for new_lot in description_data["tender"]["lots"]:
            existing_lot = next((lot for lot in tender.setdefault("lots", []) if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot["description"] = new_lot["description"]
            else:
                tender["lots"].append(new_lot)

    # Merge lotGroups
    if "lotGroups" in description_data["tender"]:
        for new_group in description_data["tender"]["lotGroups"]:
            existing_group = next((group for group in tender.setdefault("lotGroups", []) if group["id"] == new_group["id"]), None)
            if existing_group:
                existing_group["description"] = new_group["description"]
            else:
                tender["lotGroups"].append(new_group)

    # Merge tender description
    if "description" in description_data["tender"]:
        tender["description"] = description_data["tender"]["description"]