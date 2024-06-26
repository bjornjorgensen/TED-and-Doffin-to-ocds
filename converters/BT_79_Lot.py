# converters/BT_79_Lot.py

from lxml import etree

def parse_performing_staff_qualification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        curricula_code = lot.xpath("cac:TenderingTerms/cbc:RequiredCurriculaCode/text()", namespaces=namespaces)
        
        if curricula_code:
            code = curricula_code[0]
            if code in ['par-requ', 't-requ']:
                result[lot_id] = True
            elif code == 'not-requ':
                result[lot_id] = False

    return result

def merge_performing_staff_qualification(release_json, staff_qualification_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, requires_qualification in staff_qualification_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        other_requirements = lot.setdefault("otherRequirements", {})
        other_requirements["requiresStaffNamesAndQualifications"] = requires_qualification

    return release_json