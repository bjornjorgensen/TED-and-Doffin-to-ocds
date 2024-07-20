# converters/BT_198_BT_09_Procedure.py

from lxml import etree
import logging
from utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)

def parse_bt_198_bt_09_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    xpath = "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/efbc:PublicationDate"
    publication_dates = root.xpath(xpath, namespaces=namespaces)

    if publication_dates:
        date_string = publication_dates[0].text
        iso_date = convert_to_iso_format(date_string)
        return iso_date
    
    return None

def merge_bt_198_bt_09_procedure(release_json, bt_198_bt_09_procedure_data):
    if not bt_198_bt_09_procedure_data:
        logger.warning("No BT-198(BT-09)-Procedure data to merge")
        return

    if 'withheldInformation' not in release_json:
        release_json['withheldInformation'] = []

    for withheld_item in release_json['withheldInformation']:
        if withheld_item.get('id') == "BT-195(BT-09)-Procedure":
            withheld_item['availabilityDate'] = bt_198_bt_09_procedure_data
            logger.info("Merged BT-198(BT-09)-Procedure data")
            return

    # If no existing BT-09-Procedure item found, create a new one
    release_json['withheldInformation'].append({
        "id": "BT-195(BT-09)-Procedure",
        "availabilityDate": bt_198_bt_09_procedure_data
    })
    logger.info("Created new BT-198(BT-09)-Procedure withheld information item")