# converters/BT_21_Part.py

from lxml import etree

def parse_part_title(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}
    
    result = {"tender": {}}
    
    part_title = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
    
    if part_title:
        result["tender"]["title"] = part_title[0]
    
    return result if "title" in result["tender"] else None

def merge_part_title(release_json, part_title_data):
    if not part_title_data:
        return
    
    release_json.setdefault("tender", {})["title"] = part_title_data["tender"]["title"]
