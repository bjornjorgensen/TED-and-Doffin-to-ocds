# converters/BT_717_Lot_Clean_Vehicles_Directive.py
from lxml import etree

def parse_clean_vehicles_directive(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        cvd_applicable = lot.xpath(".//efac:StrategicProcurement/efbc:ApplicableLegalBasis[@listName='cvd-scope']/text()", namespaces=namespaces)
        
        if cvd_applicable and cvd_applicable[0].lower() == 'true':
            result[lot_id] = True

    return result

def merge_clean_vehicles_directive(release_json, cvd_data):
    if cvd_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, is_applicable in cvd_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            if is_applicable:
                covered_by = lot.setdefault("coveredBy", [])
                if "EU-CVD" not in covered_by:
                    covered_by.append("EU-CVD")

    return release_json