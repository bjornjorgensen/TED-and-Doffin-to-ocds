# converters/BT_25.py
from lxml import etree

def parse_quantity(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"items": []}}
    
    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        quantity = lot_element.xpath("cac:ProcurementProject/cbc:EstimatedOverallContractQuantity/text()", namespaces=namespaces)
        if quantity:
            item = {
                "relatedLot": lot_id,
                "quantity": float(quantity[0])
            }
            result["tender"]["items"].append(item)
    
    return result if result["tender"]["items"] else None

def merge_quantity(release_json, quantity_data):
    if quantity_data and "tender" in quantity_data and "items" in quantity_data["tender"]:
        existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
        for new_item in quantity_data["tender"]["items"]:
            existing_item = next((item for item in existing_items if item.get("relatedLot") == new_item["relatedLot"]), None)
            if existing_item:
                existing_item["quantity"] = new_item["quantity"]
            else:
                new_item["id"] = str(len(existing_items) + 1)
                existing_items.append(new_item)
