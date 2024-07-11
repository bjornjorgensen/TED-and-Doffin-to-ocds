# converters/BT_196_BT_171_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_justification_description_tender_bt171(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='ten-ran']/efbc:ReasonDescription"
    
    results = []
    reason_descriptions = root.xpath(xpath, namespaces=namespaces)
    
    for reason_description in reason_descriptions:
        lot_tender = reason_description.xpath("ancestor::efac:LotTender", namespaces=namespaces)[0]
        tender_id = lot_tender.xpath("cbc:ID/text()", namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})[0]
        results.append((tender_id, reason_description.text))
    
    return results

def merge_unpublished_justification_description_tender_bt171(release_json, rationale_data):
    if not rationale_data:
        return

    if "withheldInformation" not in release_json:
        release_json["withheldInformation"] = []

    for tender_id, rationale in rationale_data:
        withheld_item = next((item for item in release_json["withheldInformation"] if item.get("id") == f"ten-ran-{tender_id}"), None)
        
        if withheld_item is None:
            withheld_item = {"id": f"ten-ran-{tender_id}"}
            release_json["withheldInformation"].append(withheld_item)

        withheld_item["rationale"] = rationale