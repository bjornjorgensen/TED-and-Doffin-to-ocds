from lxml import etree

def parse_submission_url(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        submission_url = lot.xpath("cac:TenderingTerms/cac:TenderRecipientParty/cbc:EndpointID/text()", namespaces=namespaces)
        
        if submission_url:
            lot_data = {
                "id": lot_id,
                "submissionMethodDetails": submission_url[0]
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None