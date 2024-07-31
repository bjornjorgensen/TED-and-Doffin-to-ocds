# converters/BT_197_BT_539_Lot.py

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

def parse_bt_197_bt_539_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-typ']/cbc:ReasonCode"
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

def merge_bt_197_bt_539_lot(release_json, bt_197_bt_539_data):
    if not bt_197_bt_539_data:
        logger.warning("No BT-197(BT-539)-Lot data to merge")
        return

    if 'withheldInformation' not in release_json:
        release_json['withheldInformation'] = []

    for withheld_item in release_json['withheldInformation']:
        if withheld_item.get('field') == 'BT-539':
            if 'rationaleClassifications' not in withheld_item:
                withheld_item['rationaleClassifications'] = []
            withheld_item['rationaleClassifications'].extend(bt_197_bt_539_data)
            logger.info("Merged BT-197(BT-539)-Lot data")
            return

    # If no existing BT-539 item found, create a new one
    release_json['withheldInformation'].append({
        "field": "BT-539",
        "rationaleClassifications": bt_197_bt_539_data
    })
    logger.info("Created new BT-197(BT-539)-Lot withheld information item")
