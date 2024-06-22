from lxml import etree

def parse_public_opening_place(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        opening_place = lot.xpath("cac:TenderingProcess/cac:OpenTenderEvent/cac:OccurenceLocation/cbc:Description/text()", namespaces=namespaces)
        
        if opening_place:
            lot_data = {
                "id": lot_id,
                "bidOpening": {
                    "location": {
                        "description": opening_place[0]
                    }
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None