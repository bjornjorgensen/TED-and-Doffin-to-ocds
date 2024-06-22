from lxml import etree

def parse_accelerated_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    accelerated_procedure = root.xpath(
        "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReasonCode",
        namespaces=namespaces
    )
    
    if accelerated_procedure:
        is_accelerated = accelerated_procedure[0].text.lower() == 'true'
        return {
            "tender": {
                "procedure": {
                    "isAccelerated": is_accelerated
                }
            }
        }
    
    return None