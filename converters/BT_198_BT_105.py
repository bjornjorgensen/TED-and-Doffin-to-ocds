# converters/BT_198_BT_105.py

import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)

def parse_unpublished_access_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
    }
    
    xpath = "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']/efbc:PublicationDate"
    publication_date = root.xpath(xpath, namespaces=namespaces)
    
    if publication_date:
        return convert_to_iso_format(publication_date[0].text)
    return None

def convert_to_iso_format(date_string):
    # Split the date string and timezone
    date_part, _, tz_part = date_string.partition('+')
    
    # Parse the date part
    date = datetime.strptime(date_part, "%Y-%m-%d")
    
    # Set the time to 00:00:00
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Format the datetime with the original timezone
    return f"{date.isoformat()}+{tz_part}"

def merge_unpublished_access_date(release_json, access_date):
    if access_date:
        if "withheldInformation" not in release_json:
            release_json["withheldInformation"] = []
        
        # Find the existing withheldInformationItem for BT-195(BT-105)-Procedure
        existing_item = next((item for item in release_json["withheldInformation"] if item.get("field") == "procedureType"), None)
        
        if existing_item:
            existing_item["availabilityDate"] = access_date
        else:
            release_json["withheldInformation"].append({
                "field": "procedureType",
                "availabilityDate": access_date
            })