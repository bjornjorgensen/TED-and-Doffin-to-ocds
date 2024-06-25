# converters/BT_766_Dynamic_Purchasing_System.py

from lxml import etree

def parse_dynamic_purchasing_system(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    type_mapping = {
        'dps-list': 'closed',
        'dps-nlist': 'open'
    }

    result = {
        'lots': {},
        'part': None
    }

    # Parse for Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        dps_code = lot.xpath("cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='dps-usage']/cbc:ContractingSystemTypeCode/text()", namespaces=namespaces)
        
        if dps_code and dps_code[0] != 'none':
            result['lots'][lot_id] = type_mapping.get(dps_code[0])

    # Parse for Part
    part_dps_code = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='dps-usage']/cbc:ContractingSystemTypeCode/text()", namespaces=namespaces)
    
    if part_dps_code and part_dps_code[0] != 'none':
        result['part'] = type_mapping.get(part_dps_code[0])

    return result

def merge_dynamic_purchasing_system(release_json, dps_data):
    tender = release_json.setdefault("tender", {})

    # Merge for Lots
    lots = tender.setdefault("lots", [])
    for lot_id, dps_type in dps_data['lots'].items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        techniques = lot.setdefault("techniques", {})
        techniques["hasDynamicPurchasingSystem"] = True
        techniques.setdefault("dynamicPurchasingSystem", {})["type"] = dps_type

    # Merge for Part
    if dps_data['part']:
        techniques = tender.setdefault("techniques", {})
        techniques["hasDynamicPurchasingSystem"] = True
        techniques.setdefault("dynamicPurchasingSystem", {})["type"] = dps_data['part']

    return release_json