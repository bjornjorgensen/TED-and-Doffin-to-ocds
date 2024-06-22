from lxml import etree

def parse_procedure_features(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    procedure_description = root.xpath("//cac:TenderingProcess/cbc:Description", namespaces=namespaces)
    
    if procedure_description:
        description = procedure_description[0].text
        return {
            "tender": {
                "procurementMethodDetails": description
            }
        }
    
    return None