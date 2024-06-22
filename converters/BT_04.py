# converters/BT_04.py
from lxml import etree

def parse_procedure_identifier(xml_content):
    """
    Parses the XML content to extract the procedure identifier and maps it to tender.id.

    :param xml_content: The XML content as a string.
    :return: A dictionary containing the tender.id.
    """
    # Parse the XML content
    tree = etree.fromstring(xml_content)
    
    # Define the namespaces
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    # Use XPath to find the cbc:ContractFolderID element
    xpath_expr = '//cbc:ContractFolderID'
    contract_folder_id_elements = tree.xpath(xpath_expr, namespaces=namespaces)
    
    # Extract the value of the cbc:ContractFolderID element
    if contract_folder_id_elements:
        contract_folder_id = contract_folder_id_elements[0].text
    else:
        contract_folder_id = None
    
    # Construct the output JSON
    output = {
        "tender": {
            "id": contract_folder_id
        }
    }
    
    return output