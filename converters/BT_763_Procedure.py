# converters/BT_763_Procedure.py

from lxml import etree

def parse_lots_all_required(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    part_presentation_code = root.xpath("//cac:TenderingProcess/cbc:PartPresentationCode[@listName='tenderlot-presentation']/text()", namespaces=namespaces)
    
    return part_presentation_code[0] if part_presentation_code else None

def merge_lots_all_required(release_json, is_all_required):
    if is_all_required == 'all':
        tender = release_json.setdefault("tender", {})
        lot_details = tender.setdefault("lotDetails", {})
        lot_details["maximumLotsBidPerSupplier"] = 1e9999  # This is effectively infinity
    
    return release_json