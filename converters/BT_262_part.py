# BT_262_part.py

from lxml import etree

def parse_main_classification_code_part(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"items": []}}

    parts = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    
    for part in parts:
        classification = part.xpath("cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        
        if classification:
            code = classification[0].text
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "classification": {
                    "id": code
                }
            }
            result["tender"]["items"].append(item)

    return result

def merge_main_classification_code_part(release_json, classification_code_data):
    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
    
    for new_item in classification_code_data["tender"]["items"]:
        existing_item = next((item for item in existing_items if item["id"] == new_item["id"]), None)
        
        if existing_item:
            existing_item.setdefault("classification", {}).update(new_item["classification"])
        else:
            existing_items.append(new_item)