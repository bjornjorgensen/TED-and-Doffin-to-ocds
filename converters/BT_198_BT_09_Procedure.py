# converters/BT_198_BT_09_Procedure.py

from lxml import etree
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def convert_to_iso_format(date_string):
    # Split the date string and timezone
    date_part, _, tz_part = date_string.partition('+')
    # Parse the date part
    date = datetime.strptime(date_part, "%Y-%m-%d")
    # Add time component
    date = date.replace(hour=0, minute=0, second=0)
    # Format the date with the original timezone or UTC if no timezone
    if tz_part:
        return f"{date.isoformat()}+{tz_part}"
    else:
        return f"{date.isoformat()}Z"

def parse_unpublished_access_date_procedure_bt09(xml_content):
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
    
    publication_date = root.xpath(xpath, namespaces=namespaces)
    
    if publication_date:
        return convert_to_iso_format(publication_date[0].text)
    return None

def merge_unpublished_access_date_procedure_bt09(release_json, availability_date):
    if not availability_date:
        return

    for item in release_json.get("withheldInformation", []):
        if item.get("field") == "cro-bor-law":
            item["availabilityDate"] = availability_date
            break