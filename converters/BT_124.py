from lxml import etree

def parse_tool_atypical_url(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}
    lots = []

    # Parse Tool Atypical URL for lots
    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        atypical_url = lot.xpath("cac:TenderingProcess/cbc:AccessToolsURI/text()", namespaces=namespaces)
        
        if atypical_url:
            lots.append({
                "id": lot_id,
                "communication": {
                    "atypicalToolUrl": atypical_url[0]
                }
            })

    if lots:
        result["tender"]["lots"] = lots

    # Parse Tool Atypical URL for parts
    part_atypical_url = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cbc:AccessToolsURI/text()",
        namespaces=namespaces
    )

    if part_atypical_url:
        result["tender"]["communication"] = {"atypicalToolUrl": part_atypical_url[0]}

    return result if result["tender"] else None