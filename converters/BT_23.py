# converters/BT_23.py
from lxml import etree

def parse_main_nature(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}
    
    def map_procurement_category(value):
        if value in ["works", "services"]:
            return value
        elif value == "supplies":
            return "goods"
        return None

    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        procurement_type = lot_element.xpath("cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)
        if procurement_type:
            category = map_procurement_category(procurement_type[0])
            if category:
                lot = {
                    "id": lot_id,
                    "mainProcurementCategory": category
                }
                result["tender"]["lots"].append(lot)
    
    # Parse Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)
    if part_element:
        category = map_procurement_category(part_element[0])
        if category:
            result["tender"]["mainProcurementCategory"] = category
    
    # Parse Procedure
    procedure_element = root.xpath("/*/cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)
    if procedure_element:
        category = map_procurement_category(procedure_element[0])
        if category:
            result["tender"]["mainProcurementCategory"] = category
    
    return result if (result["tender"]["lots"] or "mainProcurementCategory" in result["tender"]) else None
