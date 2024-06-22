# converters/BT_03.py
from lxml import etree

def parse_form_type(xml_content):
    # Define the mapping table
    form_type_mapping = {
        'planning': {'tag': ['tender'], 'status': 'planned'},
        'competition': {'tag': ['tender'], 'status': 'active'},
        'change': {'tag': ['tenderUpdate'], 'status': ''},
        'result': {'tag': ['award', 'contract'], 'status': 'complete'},
        'dir-awa-pre': {'tag': ['award', 'contract'], 'status': 'complete'},
        'cont-modif': {'tag': ['awardUpdate', 'contractUpdate'], 'status': ''}
    }

    # Parse the XML content
    tree = etree.fromstring(xml_content)
    
    # Define the namespaces
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    # Use XPath to find the cbc:NoticeTypeCode element
    xpath_expr = '//cbc:NoticeTypeCode'
    notice_type_code = tree.xpath(xpath_expr, namespaces=namespaces)
    
    if notice_type_code:
        list_name = notice_type_code[0].get('listName')
        if list_name in form_type_mapping:
            mapping = form_type_mapping[list_name]
            return {
                "tag": mapping['tag'],
                "tender": {
                    "status": mapping['status']
                }
            }
    
    # Return default values if no matching listName is found
    return {
        "tag": [],
        "tender": {
            "status": ""
        }
    }