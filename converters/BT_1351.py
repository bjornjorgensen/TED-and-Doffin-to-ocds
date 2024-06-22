from lxml import etree

def parse_procedure_accelerated_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    accelerated_justification = root.xpath(
        "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReason/text()",
        namespaces=namespaces
    )

    if accelerated_justification:
        return {
            "tender": {
                "procedure": {
                    "acceleratedRationale": accelerated_justification[0]
                }
            }
        }

    return None