# converters/BT_197_BT_142_LotResult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

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
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-cho']/cbc:ReasonCode"
    reason_codes = root.xpath(xpath, namespaces=namespaces)

    results = []
    for reason_code in reason_codes:
        code = reason_code.text
        if code in JUSTIFICATION_CODES:
            results.append({
                "scheme": "eu-non-publication-justification",
                "id": code,
                "description": JUSTIFICATION_CODES[code]['description'],
                "uri": JUSTIFICATION_CODES[code]['uri']
            })

    return results if results else None

def merge_bt_197_bt_142_lot_result(release_json, bt_197_bt_142_data):
    if not bt_197_bt_142_data:
        logger.warning("No BT-197(BT-142)-LotResult data to merge")
        return

    if 'withheldInformation' not in release_json:
        release_json['withheldInformation'] = []

    release_json['withheldInformation'].append({
        "field": "BT-142",
        "rationaleClassifications": bt_197_bt_142_data
    })

    logger.info("Merged BT-197(BT-142)-LotResult data")