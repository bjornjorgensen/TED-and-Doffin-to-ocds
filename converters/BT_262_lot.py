# BT_262_lot.py

from lxml import etree

def parse_main_classification_code_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"items": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        classification = lot.xpath("cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode", namespaces=namespaces)
        
        if classification:
            code = classification[0].text
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "classification": {
                    "id": code
                },
                "relatedLot": lot_id
            }
            result["tender"]["items"].append(item)

    return result

def merge_main_classification_code_lot(release_json, classification_code_data):
    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
    
    for new_item in classification_code_data["tender"]["items"]:
        existing_item = next((item for item in existing_items if item.get("relatedLot") == new_item["relatedLot"]), None)
        
        if existing_item:
            existing_item.setdefault("classification", {}).update(new_item["classification"])
        else:
            existing_items.append(new_item)