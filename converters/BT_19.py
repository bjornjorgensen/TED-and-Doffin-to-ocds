from lxml import etree

JUSTIFICATION_CODES = {
    "ipr-iss": "Intellectual property right issues",
    "phy-mod": "Inclusion of a physical model",
    "sen-info": "Protection of particularly sensitive information",
    "sp-of-eq": "Buyer would need specialised office equipment",
    "tdf-non-av": "Tools, devices, or file formats not generally available"
}

def parse_submission_nonelectronic_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        justification_code = lot.xpath("cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='no-esubmission-justification']/cbc:ProcessReasonCode/text()", namespaces=namespaces)
        
        if justification_code:
            lot_data = {
                "id": lot_id,
                "submissionTerms": {
                    "nonElectronicSubmission": {
                        "rationale": JUSTIFICATION_CODES.get(justification_code[0], "Unknown justification")
                    }
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None