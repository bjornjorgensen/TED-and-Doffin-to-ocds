from lxml import etree

def parse_direct_award_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"relatedProcesses": []}

    process_justifications = root.xpath("//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']", namespaces=namespaces)
    
    for index, justification in enumerate(process_justifications, start=1):
        identifier = justification.xpath("cbc:Description/text()", namespaces=namespaces)
        reason_code = justification.xpath("cbc:ProcessReasonCode/text()", namespaces=namespaces)
        
        if identifier:
            related_process = {
                "id": str(index),
                "identifier": identifier[0],
                "scheme": "eu-oj",
                "relationship": []
            }
            
            if reason_code:
                if reason_code[0] in ["irregular", "unsuitable"]:
                    related_process["relationship"].append("unsuccessfulProcess")
                elif reason_code[0] in ["additional", "existing", "repetition"]:
                    related_process["relationship"].append("prior")
            
            result["relatedProcesses"].append(related_process)

    return result if result["relatedProcesses"] else None