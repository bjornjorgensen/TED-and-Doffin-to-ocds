# converters/BT_726_Suitable_For_SMEs.py
from lxml import etree

def parse_suitable_for_smes(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {
        'lots': {},
        'lotGroups': {},
        'tender': None
    }

    # Process Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        sme_suitable = lot.xpath("cac:ProcurementProject/cbc:SMESuitableIndicator/text()", namespaces=namespaces)
        if sme_suitable:
            result['lots'][lot_id] = sme_suitable[0].lower() == 'true'

    # Process LotGroups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup in lotgroup_elements:
        lotgroup_id = lotgroup.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        sme_suitable = lotgroup.xpath("cac:ProcurementProject/cbc:SMESuitableIndicator/text()", namespaces=namespaces)
        if sme_suitable:
            result['lotGroups'][lotgroup_id] = sme_suitable[0].lower() == 'true'

    # Process Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:SMESuitableIndicator/text()", namespaces=namespaces)
    if part_element:
        result['tender'] = part_element[0].lower() == 'true'

    return result

def merge_suitable_for_smes(release_json, sme_data):
    if sme_data:
        tender = release_json.setdefault("tender", {})

        # Merge Lots
        lots = tender.setdefault("lots", [])
        for lot_id, sme_suitable in sme_data['lots'].items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            suitability = lot.setdefault("suitability", {})
            suitability["sme"] = sme_suitable

        # Merge LotGroups
        lot_groups = tender.setdefault("lotGroups", [])
        for lotgroup_id, sme_suitable in sme_data['lotGroups'].items():
            lotgroup = next((lg for lg in lot_groups if lg.get("id") == lotgroup_id), None)
            if not lotgroup:
                lotgroup = {"id": lotgroup_id}
                lot_groups.append(lotgroup)
            suitability = lotgroup.setdefault("suitability", {})
            suitability["sme"] = sme_suitable

        # Merge Part (Tender-level)
        if sme_data['tender'] is not None:
            suitability = tender.setdefault("suitability", {})
            suitability["sme"] = sme_data['tender']

    return release_json