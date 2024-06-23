# converters/BT_58_Lot.py
from lxml import etree

def parse_renewal_maximum_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        renewal_maximum = lot.xpath("cac:ProcurementProject/cac:ContractExtension/cbc:MaximumNumberNumeric/text()", namespaces=namespaces)
        
        if renewal_maximum:
            result[lot_id] = int(renewal_maximum[0])

    return result if result else None

def merge_renewal_maximum_lot(release_json, renewal_data):
    if renewal_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, maximum_renewals in renewal_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            renewal = lot.setdefault("renewal", {})
            renewal["maximumRenewals"] = maximum_renewals

    return release_json