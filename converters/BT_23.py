# converters/BT_23.py

from lxml import etree

def parse_main_nature(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    # BT-23-Lot
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        nature = lot.xpath("cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)
        if nature:
            main_category = 'goods' if nature[0] == 'supplies' else nature[0]
            result["tender"].setdefault("lots", []).append({
                "id": lot_id,
                "mainProcurementCategory": main_category
            })

    # BT-23-Part
    part_nature = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)
    
    # BT-23-Procedure
    procedure_nature = root.xpath("//cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)

    # Combine Part and Procedure nature
    combined_nature = part_nature + procedure_nature
    if combined_nature:
        main_category = 'goods' if combined_nature[0] == 'supplies' else combined_nature[0]
        result["tender"]["mainProcurementCategory"] = main_category

    return result if result["tender"] else None

def merge_main_nature(release_json, main_nature_data):
    if not main_nature_data:
        return

    tender = release_json.setdefault("tender", {})

    # Merge lots
    if "lots" in main_nature_data["tender"]:
        for new_lot in main_nature_data["tender"]["lots"]:
            existing_lot = next((lot for lot in tender.setdefault("lots", []) if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot["mainProcurementCategory"] = new_lot["mainProcurementCategory"]
            else:
                tender["lots"].append(new_lot)

    # Merge tender mainProcurementCategory
    if "mainProcurementCategory" in main_nature_data["tender"]:
        tender["mainProcurementCategory"] = main_nature_data["tender"]["mainProcurementCategory"]