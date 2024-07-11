# converters/BT_197_BT_09_Procedure.py

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

def parse_unpublished_justification_code_procedure_bt09(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/cbc:ReasonCode"
    
    reason_code = root.xpath(xpath, namespaces=namespaces)
    
    if reason_code:
        code = reason_code[0].text
        if code in JUSTIFICATION_CODES:
            return {
                'scheme': 'non-publication-justification',
                'id': code,
                'description': JUSTIFICATION_CODES[code]['description'],
                'uri': JUSTIFICATION_CODES[code]['uri']
            }
    return None

def merge_unpublished_justification_code_procedure_bt09(release_json, justification_code):
    if not justification_code:
        return

    for item in release_json.get("withheldInformation", []):
        if item.get("field") == "cro-bor-law":
            if "rationaleClassifications" not in item:
                item["rationaleClassifications"] = []
            item["rationaleClassifications"].append(justification_code)
            break