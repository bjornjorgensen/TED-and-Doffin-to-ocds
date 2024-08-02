# converters/BT_195_BT_773_Tender.py

from lxml import etree

def parse_unpublished_subcontracting_tender_bt773(xml_content):
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

    withheld_info = []

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-con']"
    
    for element in root.xpath(xpath, namespaces=namespaces):
        field_code = element.xpath("efbc:FieldIdentifierCode/text()", namespaces=namespaces)[0]
        tender_id = element.xpath("ancestor::efac:LotTender/cbc:ID/text()", namespaces=namespaces)[0]
        
        withheld_info.append({
            "id": f"{field_code}-{tender_id}",
            "field": field_code,
            "name": "Subcontracting"
        })

    return {"withheldInformation": withheld_info} if withheld_info else None

def merge_unpublished_subcontracting_tender_bt773(release_json, withheld_info_data):
    if not withheld_info_data:
        return

    release_json.setdefault("withheldInformation", []).extend(withheld_info_data["withheldInformation"])