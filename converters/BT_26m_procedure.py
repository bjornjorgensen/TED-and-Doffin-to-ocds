# BT_26m_procedure.py

from lxml import etree

def parse_main_classification_type_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"items": []}}

    classifications = root.xpath("//cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
    
    if classifications:
        scheme = classifications[0].get("listName", "").upper()
        if scheme:
            item = {
                "id": "1",
                "classification": {
                    "scheme": scheme
                }
            }
            result["tender"]["items"].append(item)

    return result

def merge_main_classification_type_procedure(release_json, classification_type_data):
    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
    
    for new_item in classification_type_data["tender"]["items"]:
        existing_item = next((item for item in existing_items if item["id"] == new_item["id"]), None)
        
        if existing_item:
            existing_item["classification"] = new_item["classification"]
        else:
            existing_items.append(new_item)