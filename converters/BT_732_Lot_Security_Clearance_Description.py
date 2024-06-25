# converters/BT_732_Lot_Security_Clearance_Description.py
from lxml import etree

def parse_security_clearance_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        security_clearance = lot.xpath(".//cac:SecurityClearanceTerm/cbc:Description/text()", namespaces=namespaces)
        
        if security_clearance:
            result[lot_id] = security_clearance[0]

    return result

def merge_security_clearance_description(release_json, security_clearance_data):
    if security_clearance_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, description in security_clearance_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            other_requirements = lot.setdefault("otherRequirements", {})
            other_requirements["securityClearance"] = description

    return release_json