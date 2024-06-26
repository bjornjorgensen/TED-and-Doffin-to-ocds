# converters/BT_777_Lot.py

from lxml import etree

def parse_strategic_procurement_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        descriptions = lot.xpath("cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='strategic-procurement']/cbc:ProcurementType/text()", namespaces=namespaces)
        
        if descriptions:
            result[lot_id] = descriptions

    return result

def merge_strategic_procurement_description(release_json, strategic_procurement_data):
    if not strategic_procurement_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, descriptions in strategic_procurement_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        sustainability = lot.setdefault("sustainability", [])
        
        for description in descriptions:
            # Check if there's an existing sustainability object without a description
            existing_sustainability = next((s for s in sustainability if 'description' not in s), None)
            if existing_sustainability:
                existing_sustainability['description'] = description
            else:
                sustainability.append({"description": description})

    return release_json