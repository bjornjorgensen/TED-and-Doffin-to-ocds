# converters/BT_13_Lot.py

import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)

def parse_additional_info_deadline(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}
    
    lots_data = []
    
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        end_date = lot.xpath("cac:TenderingProcess/cac:AdditionalInformationRequestPeriod/cbc:EndDate/text()", namespaces=namespaces)
        end_time = lot.xpath("cac:TenderingProcess/cac:AdditionalInformationRequestPeriod/cbc:EndTime/text()", namespaces=namespaces)
        
        if end_date and end_time:
            iso_date = convert_to_iso_format(end_date[0], end_time[0])
            lots_data.append({"id": lot_id, "enquiryPeriod": {"endDate": iso_date}})
    
    return lots_data if lots_data else None

def convert_to_iso_format(date_string, time_string):
    # Combine date and time
    datetime_string = f"{date_string.split('+')[0]}T{time_string}"
    
    # Parse the datetime
    date_time = datetime.fromisoformat(datetime_string)
    
    # Format the datetime with the original timezone
    return date_time.isoformat()

def merge_additional_info_deadline(release_json, lots_data):
    if lots_data:
        if "tender" not in release_json:
            release_json["tender"] = {}
        if "lots" not in release_json["tender"]:
            release_json["tender"]["lots"] = []
        
        for lot_data in lots_data:
            existing_lot = next((lot for lot in release_json["tender"]["lots"] if lot["id"] == lot_data["id"]), None)
            if existing_lot:
                existing_lot["enquiryPeriod"] = lot_data["enquiryPeriod"]
            else:
                release_json["tender"]["lots"].append(lot_data)