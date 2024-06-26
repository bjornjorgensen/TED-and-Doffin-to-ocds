# converters/BT_776_Lot.py

from lxml import etree

def parse_procurement_innovation(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    innovative_acquisition_mapping = {
        'mar-nov': 'economic.marketInnovationPromotion',
        'proc-innov': 'economic.processInnovation',
        'prod-innov': 'economic.productInnovation',
        'rd-act': 'economic.researchDevelopmentActivities'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        innovation_codes = lot.xpath("cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='innovative-acquisition']/cbc:ProcurementTypeCode/text()", namespaces=namespaces)
        
        if innovation_codes:
            result[lot_id] = [innovative_acquisition_mapping.get(code) for code in innovation_codes if code in innovative_acquisition_mapping]

    return result

def merge_procurement_innovation(release_json, procurement_innovation_data):
    if not procurement_innovation_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, sustainability_goals in procurement_innovation_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        lot["hasSustainability"] = True
        sustainability = lot.setdefault("sustainability", [])
        for goal in sustainability_goals:
            sustainability.append({"goal": goal})

    return release_json