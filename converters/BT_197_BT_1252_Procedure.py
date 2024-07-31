# converters/BT_197_BT_1252_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

# Authority table for justification codes
JUSTIFICATION_CODES = {
    'eo-int': {
        'description': 'Commercial interests of an economic operator',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/eo-int'
    },
    'fair-comp': {
        'description': 'Fair competition',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/fair-comp'
    },
    'law-enf': {
        'description': 'Law enforcement',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/law-enf'
    },
    'oth-int': {
        'description': 'Other public interest',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int'
    },
    'rd-ser': {
        'description': 'Research and development (R&D) services',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/rd-ser'
    }
}

def parse_unpublished_justification_code_procedure_bt1252(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    xpath = "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='dir-awa-pre']/cbc:ReasonCode"
    
    reason_code = root.xpath(xpath, namespaces=namespaces)
    
    if reason_code:
        code = reason_code[0].text
        if code in JUSTIFICATION_CODES:
            return {
                'scheme': 'eu-non-publication-justification',
                'id': code,
                'description': JUSTIFICATION_CODES[code]['description'],
                'uri': JUSTIFICATION_CODES[code]['uri']
            }
    return None

def merge_unpublished_justification_code_procedure_bt1252(release_json, justification_code):
    if not justification_code:
        return

    withheld_info = next((item for item in release_json.get("withheldInformation", []) if item.get("field") == "dir-awa-pre"), None)
    
    if withheld_info:
        if "rationaleClassifications" not in withheld_info:
            withheld_info["rationaleClassifications"] = []
        withheld_info["rationaleClassifications"].append(justification_code)