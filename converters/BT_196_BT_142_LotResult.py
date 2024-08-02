# converters/BT_196_BT_142_LotResult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_justification_description_lotresult_bt142(xml_content):
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

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-cho']/efbc:ReasonDescription"
    
    results = []
    reason_descriptions = root.xpath(xpath, namespaces=namespaces)
    
    for reason_description in reason_descriptions:
        lot_result = reason_description.xpath("ancestor::efac:LotResult", namespaces=namespaces)[0]
        lot_id = lot_result.xpath("cbc:ID/text()", namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})[0]
        results.append((lot_id, reason_description.text))
    
    return results

def merge_unpublished_justification_description_lotresult_bt142(release_json, rationale_data):
    if not rationale_data:
        return

    if "withheldInformation" not in release_json:
        release_json["withheldInformation"] = []

    for lot_id, rationale in rationale_data:
        withheld_item = next((item for item in release_json["withheldInformation"] if item.get("id") == f"win-cho-{lot_id}"), None)
        
        if withheld_item is None:
            withheld_item = {"id": f"win-cho-{lot_id}"}
            release_json["withheldInformation"].append(withheld_item)

        withheld_item["rationale"] = rationale