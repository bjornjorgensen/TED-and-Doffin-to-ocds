# converters/BT_54_Lot.py
from lxml import etree

def parse_options_description_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        options_description = lot.xpath("./cac:ProcurementProject/cac:ContractExtension/cbc:OptionsDescription/text()", namespaces=namespaces)
        
        if options_description:
            result[lot_id] = options_description[0]

    return result if result else None

def merge_options_description_lot(release_json, options_data):
    if options_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, description in options_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            options = lot.setdefault("options", {})
            options["description"] = description

    return release_json