# converters/BT_196_BT_106_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_justification_description_procedure_bt106(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc']/efbc:ReasonDescription"
    
    reason_description = root.xpath(xpath, namespaces=namespaces)
    
    if reason_description:
        return reason_description[0].text
    return None

def merge_unpublished_justification_description_procedure_bt106(release_json, rationale):
    if not rationale:
        return

    for item in release_json.get("withheldInformation", []):
        if item.get("field") == "pro-acc":
            item["rationale"] = rationale
            break