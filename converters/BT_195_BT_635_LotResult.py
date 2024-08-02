# converters/BT_195_BT_635_LotResult.py

from lxml import etree

def parse_unpublished_buyer_review_request_count_lotresult_bt635(xml_content):
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

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='buy-rev-cou']"
    
    for element in root.xpath(xpath, namespaces=namespaces):
        field_code = element.xpath("efbc:FieldIdentifierCode/text()", namespaces=namespaces)[0]
        lot_id = element.xpath("ancestor::efac:LotResult/cbc:ID/text()", namespaces=namespaces)[0]
        
        withheld_info.append({
            "id": f"{field_code}-{lot_id}",
            "field": field_code,
            "name": "Buyer Review Request Count"
        })

    return {"withheldInformation": withheld_info} if withheld_info else None

def merge_unpublished_buyer_review_request_count_lotresult_bt635(release_json, withheld_info_data):
    if not withheld_info_data:
        return

    release_json.setdefault("withheldInformation", []).extend(withheld_info_data["withheldInformation"])