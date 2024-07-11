# converters/BT_196_BT_105_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_justification_description_procedure_bt105(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']/efbc:ReasonDescription"
    
    reason_description = root.xpath(xpath, namespaces=namespaces)
    
    if reason_description:
        return reason_description[0].text
    return None

def merge_unpublished_justification_description_procedure_bt105(release_json, rationale):
    if not rationale:
        return

    for item in release_json.get("withheldInformation", []):
        if item.get("id", "").startswith("pro-typ-"):
            item["rationale"] = rationale
            break