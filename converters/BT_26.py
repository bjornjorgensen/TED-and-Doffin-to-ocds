# converters/BT_26.py
from lxml import etree

def parse_classifications(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"items": []}}
    
    def add_or_update_item(items, related_lot=None):
        item = next((item for item in items if item.get("relatedLot") == related_lot), None)
        if not item:
            item = {"id": str(len(items) + 1)}
            if related_lot:
                item["relatedLot"] = related_lot
            items.append(item)
        return item
    
    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        item = add_or_update_item(result["tender"]["items"], lot_id)
        
        # BT-262-Lot: Main Classification Code
        main_classification = lot_element.xpath("cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        if main_classification:
            item["classification"] = {
                "scheme": main_classification[0].get("listName", "").upper(),  # BT-26(m)-Lot: Classification Type
                "id": main_classification[0].text  # BT-262-Lot: Main Classification Code
            }
        
        # BT-263-Lot: Additional Classification Code
        additional_classifications = lot_element.xpath("cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        if additional_classifications:
            item.setdefault("additionalClassifications", [])
            for classification in additional_classifications:
                item["additionalClassifications"].append({
                    "scheme": classification.get("listName", "").upper(),  # BT-26(a)-Lot: Classification Type
                    "id": classification.text  # BT-263-Lot: Additional Classification Code
                })
    
    # Parse Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject", namespaces=namespaces)
    if part_element:
        item = add_or_update_item(result["tender"]["items"])
        
        # BT-262-Part: Main Classification Code
        main_classification = part_element[0].xpath("cac:MainCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        if main_classification:
            item["classification"] = {
                "scheme": main_classification[0].get("listName", "").upper(),  # BT-26(m)-Part: Classification Type
                "id": main_classification[0].text  # BT-262-Part: Main Classification Code
            }
        
        # BT-263-Part: Additional Classification Code
        additional_classifications = part_element[0].xpath("cac:AdditionalCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        if additional_classifications:
            item.setdefault("additionalClassifications", [])
            for classification in additional_classifications:
                item["additionalClassifications"].append({
                    "scheme": classification.get("listName", "").upper(),  # BT-26(a)-Part: Classification Type
                    "id": classification.text  # BT-263-Part: Additional Classification Code
                })
    
    # Parse Procedure
    procedure_element = root.xpath("/*/cac:ProcurementProject", namespaces=namespaces)
    if procedure_element:
        item = add_or_update_item(result["tender"]["items"])
        
        # BT-262-Procedure: Main Classification Code
        main_classification = procedure_element[0].xpath("cac:MainCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        if main_classification:
            item["classification"] = {
                "scheme": main_classification[0].get("listName", "").upper(),  # BT-26(m)-Procedure: Classification Type
                "id": main_classification[0].text  # BT-262-Procedure: Main Classification Code
            }
        
        # BT-263-Procedure: Additional Classification Code
        additional_classifications = procedure_element[0].xpath("cac:AdditionalCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        if additional_classifications:
            item.setdefault("additionalClassifications", [])
            for classification in additional_classifications:
                item["additionalClassifications"].append({
                    "scheme": classification.get("listName", "").upper(),  # BT-26(a)-Procedure: Classification Type
                    "id": classification.text  # BT-263-Procedure: Additional Classification Code
                })
    
    return result if result["tender"]["items"] else None

# The merge_classifications function remains the same
def merge_classifications(release_json, classification_data):
    if classification_data and "tender" in classification_data and "items" in classification_data["tender"]:
        existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
        for new_item in classification_data["tender"]["items"]:
            existing_item = next((item for item in existing_items if item.get("relatedLot") == new_item.get("relatedLot")), None)
            if existing_item:
                if "classification" in new_item:
                    existing_item["classification"] = new_item["classification"]
                if "additionalClassifications" in new_item:
                    existing_item.setdefault("additionalClassifications", []).extend(new_item["additionalClassifications"])
            else:
                existing_items.append(new_item)
