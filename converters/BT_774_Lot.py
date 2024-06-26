# converters/BT_774_Lot.py

from lxml import etree

def parse_green_procurement(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    environmental_impact_mapping = {
        'biodiv-eco': 'environmental.biodiversityProtectionRestoration',
        'circ-econ': 'environmental.circularEconomy',
        'clim-adapt': 'environmental.climateChangeAdaptation',
        'clim-mitig': 'environmental.climateChangeMitigation',
        'other': 'environmental',
        'pollu-prev': 'environmental.pollutionPrevention',
        'water-mar': 'environmental.waterResources'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        impact_codes = lot.xpath("cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='environmental-impact']/cbc:ProcurementTypeCode/text()", namespaces=namespaces)
        
        if impact_codes:
            result[lot_id] = [environmental_impact_mapping.get(code, 'environmental') for code in impact_codes]

    return result

def merge_green_procurement(release_json, green_procurement_data):
    if not green_procurement_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, sustainability_goals in green_procurement_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        lot["hasSustainability"] = True
        lot["sustainability"] = [{"goal": goal} for goal in sustainability_goals]

    return release_json