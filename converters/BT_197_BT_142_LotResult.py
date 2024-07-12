# converters/BT_197_BT_142_LotResult.py

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

def parse_bt_197_bt_142_lot_result(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-cho']/cbc:ReasonCode"
    
    results = []
    reason_codes = root.xpath(xpath, namespaces=namespaces)
    
    for reason_code in reason_codes:
        lot_id = reason_code.xpath("ancestor::efac:LotResult/cbc:ID/text()", namespaces=namespaces)
        code = reason_code.text
        if code in JUSTIFICATION_CODES:
            results.append({
                'lotId': lot_id[0] if lot_id else None,
                'classification': {
                    'scheme': 'eu-non-publication-justification',
                    'id': code,
                    'description': JUSTIFICATION_CODES[code]['description'],
                    'uri': JUSTIFICATION_CODES[code]['uri']
                }
            })
    
    return results if results else None

def merge_bt_197_bt_142_lot_result(release_json, justification_codes):
    if not justification_codes:
        return

    withheld_info = release_json.get("withheldInformation", [])

    for justification in justification_codes:
        lot_id = justification['lotId']
        classification = justification['classification']
        
        existing_item = next((item for item in withheld_info if item.get("id") == f"win-cho-{lot_id}"), None)
        
        if existing_item:
            if "rationaleClassifications" not in existing_item:
                existing_item["rationaleClassifications"] = []
            existing_item["rationaleClassifications"].append(classification)