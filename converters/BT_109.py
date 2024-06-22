from lxml import etree

def parse_framework_duration_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    lots = []
    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        justification = lot.xpath("cac:TenderingProcess/cac:FrameworkAgreement/cbc:Justification/text()", namespaces=namespaces)
        
        if justification:
            lots.append({
                "id": lot_id,
                "techniques": {
                    "frameworkAgreement": {
                        "periodRationale": justification[0]
                    }
                }
            })
    
    if lots:
        return {
            "tender": {
                "lots": lots
            }
        }
    
    return None