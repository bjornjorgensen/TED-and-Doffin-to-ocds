from lxml import etree

def parse_additional_nature(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    result = {"tender": {"lots": [], "additionalProcurementCategories": []}}
    
    def get_lot(lot_id):
        for lot in result["tender"]["lots"]:
            if lot["id"] == lot_id:
                return lot
        new_lot = {"id": lot_id, "additionalProcurementCategories": []}
        result["tender"]["lots"].append(new_lot)
        return new_lot

    # Parse Lots
    lot_elements = root.xpath("/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='contract-nature']/cbc:ProcurementTypeCode", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID/text()", namespaces=namespaces)[0]
        additional_type = lot_element.text
        lot = get_lot(lot_id)
        if additional_type not in lot["additionalProcurementCategories"]:
            lot["additionalProcurementCategories"].append(additional_type)
    
    # Parse Parts
    part_elements = root.xpath("/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='contract-nature']/cbc:ProcurementTypeCode", namespaces=namespaces)
    for part_element in part_elements:
        additional_type = part_element.text
        if additional_type not in result["tender"]["additionalProcurementCategories"]:
            result["tender"]["additionalProcurementCategories"].append(additional_type)
    
    # Parse Procedure
    procedure_elements = root.xpath("/*/cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='contract-nature']/cbc:ProcurementTypeCode", namespaces=namespaces)
    for procedure_element in procedure_elements:
        additional_type = procedure_element.text
        if additional_type not in result["tender"]["additionalProcurementCategories"]:
            result["tender"]["additionalProcurementCategories"].append(additional_type)
    
    return result if (result["tender"]["lots"] or result["tender"]["additionalProcurementCategories"]) else None

def merge_additional_nature(release_json, additional_nature_data):
    if additional_nature_data and "tender" in additional_nature_data:
        tender = release_json.setdefault("tender", {})
        
        # Merge Lots
        if "lots" in additional_nature_data["tender"]:
            existing_lots = tender.setdefault("lots", [])
            for new_lot in additional_nature_data["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot.setdefault("additionalProcurementCategories", []).extend(
                        cat for cat in new_lot["additionalProcurementCategories"]
                        if cat not in existing_lot["additionalProcurementCategories"]
                    )
                else:
                    existing_lots.append(new_lot)
        
        # Merge additionalProcurementCategories (Part and Procedure)
        if "additionalProcurementCategories" in additional_nature_data["tender"]:
            existing_categories = tender.setdefault("additionalProcurementCategories", [])
            for new_category in additional_nature_data["tender"]["additionalProcurementCategories"]:
                if new_category not in existing_categories:
                    existing_categories.append(new_category)
