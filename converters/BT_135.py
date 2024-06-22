from lxml import etree

def parse_direct_award_justification_text(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    justification_text = root.xpath(
        "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/cbc:ProcessReason/text()",
        namespaces=namespaces
    )

    if justification_text:
        return {
            "tender": {
                "procurementMethodRationale": justification_text[0]
            }
        }

    return None