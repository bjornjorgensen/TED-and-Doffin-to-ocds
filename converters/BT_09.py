from lxml import etree
import json

def parse_xml_to_json(xml_string):
    # Parse the XML string
    root = etree.fromstring(xml_string)
    
    # Define the namespace
    namespace = {'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                 'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}
    
    # Define the XPath expression
    xpath_expr = './/cac:ProcurementLegislationDocumentReference[cbc:ID="CrossBorderLaw"]/cbc:DocumentDescription'
    
    # Find the relevant elements using XPath
    cross_border_law_element = root.find(xpath_expr, namespaces=namespace)
    
    # Initialize the JSON structure
    json_data = {"tender": {}}
    
    # Check if the element exists and extract the text
    if cross_border_law_element is not None and cross_border_law_element.text:
        json_data["tender"]["crossBorderLaw"] = cross_border_law_element.text
    
    return json.dumps(json_data, indent=4)