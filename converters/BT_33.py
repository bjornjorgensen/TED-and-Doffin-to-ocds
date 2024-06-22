# converters/BT_33.py
from lxml import etree

def parse_lots_max_awarded(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {}}
    
    # Parse Lots Max Awarded
    max_lots_awarded_element = root.xpath("/*/cac:TenderingTerms/cac:LotDistribution/cbc:MaximumLotsAwardedNumeric", namespaces=namespaces)
    if max_lots_awarded_element:
        result["tender"]["lotDetails"] = {
            "maximumLotsAwardedPerSupplier": int(max_lots_awarded_element[0].text)
        }
    
    return result if "lotDetails" in result["tender"] else None

def merge_lots_max_awarded(release_json, lots_max_awarded_data):
    if lots_max_awarded_data and "tender" in lots_max_awarded_data and "lotDetails" in lots_max_awarded_data["tender"]:
        tender = release_json.setdefault("tender", {})
        lot_details = tender.setdefault("lotDetails", {})
        lot_details["maximumLotsAwardedPerSupplier"] = lots_max_awarded_data["tender"]["lotDetails"]["maximumLotsAwardedPerSupplier"]
