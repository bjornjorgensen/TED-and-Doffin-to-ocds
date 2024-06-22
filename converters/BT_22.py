# converters/BT_22.py
from lxml import etree

def parse_internal_identifiers(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": [], "lotGroups": [], "identifiers": []}}
    
    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        internal_id = lot_element.xpath("cac:ProcurementProject/cbc:ID[@schemeName='InternalID']/text()", namespaces=namespaces)
        if internal_id:
            lot = {
                "id": lot_id,
                "identifiers": [{"id": internal_id[0], "scheme": "internal"}]
            }
            result["tender"]["lots"].append(lot)
    
    # Parse Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup_element in lotgroup_elements:
        lotgroup_id = lotgroup_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        internal_id = lotgroup_element.xpath("cac:ProcurementProject/cbc:ID[@schemeName='InternalID']/text()", namespaces=namespaces)
        if internal_id:
            lotgroup = {
                "id": lotgroup_id,
                "identifiers": [{"id": internal_id[0], "scheme": "internal"}]
            }
            result["tender"]["lotGroups"].append(lotgroup)
    
    # Parse Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:ID[@schemeName='InternalID']", namespaces=namespaces)
    if part_element:
        result["tender"]["identifiers"].append({"id": part_element[0].text, "scheme": "internal"})
    
    # Parse Procedure
    procedure_element = root.xpath("/*/cac:ProcurementProject/cbc:ID[@schemeName='InternalID']", namespaces=namespaces)
    if procedure_element:
        result["tender"]["identifiers"].append({"id": procedure_element[0].text, "scheme": "internal"})
    
    return result if (result["tender"]["lots"] or result["tender"]["lotGroups"] or result["tender"]["identifiers"]) else None
