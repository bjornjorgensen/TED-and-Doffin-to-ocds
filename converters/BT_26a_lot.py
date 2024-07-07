# converters/BT_26a_lot.py

from lxml import etree

def parse_classification_type(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"items": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        classifications = lot.xpath("cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        
        if classifications:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "additionalClassifications": [],
                "relatedLot": lot_id
            }
            
            for classification in classifications:
                scheme = classification.get("listName", "").upper()
                if scheme:
                    item["additionalClassifications"].append({"scheme": scheme})
            
            if item["additionalClassifications"]:
                result["tender"]["items"].append(item)

    return result

def merge_classification_type(release_json, classification_type_data):
    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
    
    for new_item in classification_type_data["tender"]["items"]:
        existing_item = next((item for item in existing_items if item["relatedLot"] == new_item["relatedLot"]), None)
        
        if existing_item:
            existing_classifications = existing_item.setdefault("additionalClassifications", [])
            for new_classification in new_item["additionalClassifications"]:
                if new_classification not in existing_classifications:
                    existing_classifications.append(new_classification)
        else:
            existing_items.append(new_item)