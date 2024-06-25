# converters/BT_756_Procedure.py

from lxml import etree

def parse_pin_competition_termination(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    terminated_indicator = root.xpath("//cac:TenderingProcess/cbc:TerminatedIndicator/text()", namespaces=namespaces)
    
    if terminated_indicator and terminated_indicator[0].lower() == 'true':
        return True
    return False

def merge_pin_competition_termination(release_json, is_terminated):
    if is_terminated:
        tender = release_json.setdefault("tender", {})
        tender["status"] = "complete"
    
    return release_json