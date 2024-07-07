# converters/BT_21_Procedure.py

from lxml import etree

def parse_procedure_title(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {}}
    
    procedure_title = root.xpath("/*/cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
    
    if procedure_title:
        result["tender"]["title"] = procedure_title[0]
    
    return result if "title" in result["tender"] else None

def merge_procedure_title(release_json, procedure_title_data):
    if not procedure_title_data:
        return
    
    release_json.setdefault("tender", {})["title"] = procedure_title_data["tender"]["title"]
