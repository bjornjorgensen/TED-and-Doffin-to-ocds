# converters/BT_57_Lot.py
from lxml import etree

def parse_renewal_description_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        renewal_description = lot.xpath("cac:ProcurementProject/cac:ContractExtension/cac:Renewal/cac:Period/cbc:Description/text()", namespaces=namespaces)
        
        if renewal_description:
            result[lot_id] = renewal_description[0]

    return result if result else None

def merge_renewal_description_lot(release_json, renewal_data):
    if renewal_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, description in renewal_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            renewal = lot.setdefault("renewal", {})
            renewal["description"] = description

    return release_json