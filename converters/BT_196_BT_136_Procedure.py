# converters/BT_196_BT_136_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_justification_description_procedure_bt136(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='dir-awa-jus']/efbc:ReasonDescription"
    
    reason_description = root.xpath(xpath, namespaces=namespaces)
    
    if reason_description:
        return reason_description[0].text
    return None

def merge_unpublished_justification_description_procedure_bt136(release_json, rationale):
    if not rationale:
        return

    if "withheldInformation" not in release_json:
        release_json["withheldInformation"] = []

    withheld_item = next((item for item in release_json["withheldInformation"] if item.get("id", "").startswith("dir-awa-jus-")), None)
    
    if withheld_item is None:
        withheld_item = {"id": "dir-awa-jus-1"}
        release_json["withheldInformation"].append(withheld_item)

    withheld_item["rationale"] = rationale