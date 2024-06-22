from lxml import etree

def parse_no_negotiation_necessary(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    lots = []
    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        no_negotiation = lot.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cbc:NoFurtherNegotiationIndicator/text()",
            namespaces=namespaces
        )
        
        if no_negotiation:
            lots.append({
                "id": lot_id,
                "secondStage": {
                    "noNegotiationNecessary": no_negotiation[0].lower() == 'true'
                }
            })

    return {"tender": {"lots": lots}} if lots else None