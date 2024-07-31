# converters/BT_198_BT_106_Procedure.py

from lxml import etree
import logging
from utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)

def parse_bt_198_bt_106_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    xpath = "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc']/efbc:PublicationDate"
    publication_dates = root.xpath(xpath, namespaces=namespaces)

    if publication_dates:
        date_string = publication_dates[0].text
        iso_date = convert_to_iso_format(date_string)
        return {"availabilityDate": iso_date}
    
    return None

def merge_bt_198_bt_106_procedure(release_json, bt_198_bt_106_procedure_data):
    if not bt_198_bt_106_procedure_data:
        logger.warning("No BT-198(BT-106)-Procedure data to merge")
        return

    if 'withheldInformation' not in release_json:
        release_json['withheldInformation'] = []

    existing_item = next((item for item in release_json['withheldInformation'] if 'availabilityDate' in item), None)

    if existing_item:
        existing_item.update(bt_198_bt_106_procedure_data)
        logger.info("Updated existing BT-198(BT-106)-Procedure data")
    else:
        release_json['withheldInformation'].append(bt_198_bt_106_procedure_data)
        logger.info("Added new BT-198(BT-106)-Procedure withheld information item")