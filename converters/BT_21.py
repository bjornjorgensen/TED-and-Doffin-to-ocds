# converters/BT_21.py
from lxml import etree

def parse_lot_lotgroup_part_and_procedure_title(xml_content):
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
        lot_name = lot_element.xpath("cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
        
        if lot_name:
            lot = {
                "id": lot_id,
                "title": lot_name[0]
            }
            result["tender"]["lots"].append(lot)
    
    # Parse Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    
    for lotgroup_element in lotgroup_elements:
        lotgroup_id = lotgroup_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        lotgroup_name = lotgroup_element.xpath("cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
        
        if lotgroup_name:
            lotgroup = {
                "id": lotgroup_id,
                "title": lotgroup_name[0]
            }
            result["tender"]["lotGroups"].append(lotgroup)
    
    # Parse Part (tender title)
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Name", namespaces=namespaces)
    
    if part_element:
        result["tender"]["title"] = part_element[0].text
    
    # Parse Procedure (tender title)
    procedure_element = root.xpath("/*/cac:ProcurementProject/cbc:Name", namespaces=namespaces)
    
    if procedure_element:
        result["tender"]["title"] = procedure_element[0].text
    
    return result if (result["tender"].get("lots") or result["tender"].get("lotGroups") or "title" in result["tender"]) else None
