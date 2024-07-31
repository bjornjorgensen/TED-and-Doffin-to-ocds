# converters/BT_198_BT_105_Procedure.py

from lxml import etree
import logging
from utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)

def parse_bt_198_bt_105_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    xpath = "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']/efbc:PublicationDate"
    publication_dates = root.xpath(xpath, namespaces=namespaces)

    if publication_dates:
        date_string = publication_dates[0].text
        iso_date = convert_to_iso_format(date_string)
        return iso_date
    
    return None

def merge_bt_198_bt_105_procedure(release_json, bt_198_bt_105_procedure_data):
    if not bt_198_bt_105_procedure_data:
        logger.warning("No BT-198(BT-105)-Procedure data to merge")
        return

    if 'withheldInformation' not in release_json:
        logger.warning("No withheldInformation found to merge BT-198(BT-105)-Procedure data")
        return

    existing_item = next((item for item in release_json['withheldInformation'] if item.get('id') == "pro-typ-1"), None)

    if existing_item and 'rationaleClassifications' in existing_item:
        for classification in existing_item['rationaleClassifications']:
            classification['availabilityDate'] = bt_198_bt_105_procedure_data
        logger.info("Merged BT-198(BT-105)-Procedure data")
    else:
        logger.warning("No suitable withheldInformation item found to merge BT-198(BT-105)-Procedure data")