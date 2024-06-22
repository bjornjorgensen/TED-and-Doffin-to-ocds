from lxml import etree

def parse_procurement_procedure_type(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    procedure_code = root.xpath("//cac:TenderingProcess/cbc:ProcedureCode", namespaces=namespaces)
    
    if procedure_code:
        code = procedure_code[0].text
        procurement_method_mapping = {
            'open': 'open',
            'comp-dial': 'selective',
            'comp-tend': 'selective',
            'innovation': 'selective',
            'neg-w-call': 'selective',
            'restricted': 'selective',
            'neg-wo-call': 'limited'
        }
        
        procurement_method = procurement_method_mapping.get(code)
        
        if procurement_method:
            return {
                "tender": {
                    "procurementMethod": procurement_method
                }
            }
    
    return None