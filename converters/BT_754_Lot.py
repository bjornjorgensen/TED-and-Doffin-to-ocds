# converters/BT_754_Lot.py

from lxml import etree

def parse_accessibility(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        accessibility_code = lot.xpath("cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='accessibility']/cbc:ProcurementTypeCode/text()", namespaces=namespaces)
        
        if accessibility_code:
            accessibility_data = {}
            if accessibility_code[0] == 'inc':
                accessibility_data['hasAccessibilityCriteria'] = True
            else:
                accessibility_data['hasAccessibilityCriteria'] = False
                if accessibility_code[0] == 'n-inc':
                    accessibility_data['noAccessibilityCriteriaRationale'] = "Procurement is not intended for use by natural persons"
            
            result[lot_id] = accessibility_data

    return result

def merge_accessibility(release_json, accessibility_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, accessibility_info in accessibility_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        lot.update(accessibility_info)

    return release_json