from lxml import etree

def parse_submission_electronic(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        submission_method = lot.xpath("cac:TenderingProcess/cbc:SubmissionMethodCode[@listName='esubmission']/text()", namespaces=namespaces)
        
        if submission_method:
            lot_data = {
                "id": lot_id,
                "submissionTerms": {
                    "electronicSubmissionPolicy": submission_method[0]
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None