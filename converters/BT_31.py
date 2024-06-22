# converters/BT_31.py
from lxml import etree

def parse_lots_max_allowed(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {}}
    
    # Parse Lots Max Allowed
    max_lots_element = root.xpath("/*/cac:TenderingTerms/cac:LotDistribution/cbc:MaximumLotsSubmittedNumeric", namespaces=namespaces)
    if max_lots_element:
        result["tender"]["lotDetails"] = {
            "maximumLotsBidPerSupplier": int(max_lots_element[0].text)
        }
    
    return result if "lotDetails" in result["tender"] else None

def merge_lots_max_allowed(release_json, lots_max_allowed_data):
    if lots_max_allowed_data and "tender" in lots_max_allowed_data and "lotDetails" in lots_max_allowed_data["tender"]:
        tender = release_json.setdefault("tender", {})
        lot_details = tender.setdefault("lotDetails", {})
        lot_details["maximumLotsBidPerSupplier"] = lots_max_allowed_data["tender"]["lotDetails"]["maximumLotsBidPerSupplier"]
