# converters/BT_24.py
from lxml import etree

def parse_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": [], "lotGroups": []}}
    
    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot_element.xpath("cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
        if description:
            lot = {
                "id": lot_id,
                "description": description[0]
            }
            result["tender"]["lots"].append(lot)
    
    # Parse Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup_element in lotgroup_elements:
        lotgroup_id = lotgroup_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lotgroup_element.xpath("cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
        if description:
            lotgroup = {
                "id": lotgroup_id,
                "description": description[0]
            }
            result["tender"]["lotGroups"].append(lotgroup)
    
    # Parse Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
    if part_element:
        result["tender"]["description"] = part_element[0]
    
    # Parse Procedure
    procedure_element = root.xpath("/*/cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
    if procedure_element:
        result["tender"]["description"] = procedure_element[0]
    
    return result if (result["tender"]["lots"] or result["tender"]["lotGroups"] or "description" in result["tender"]) else None
