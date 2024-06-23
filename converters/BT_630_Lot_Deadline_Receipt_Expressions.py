# converters/BT_630_Lot_Deadline_Receipt_Expressions.py
from lxml import etree
from datetime import datetime, timedelta

def parse_lot_deadline_receipt_expressions(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        end_date = lot.xpath(".//efac:InterestExpressionReceptionPeriod/cbc:EndDate/text()", namespaces=namespaces)
        end_time = lot.xpath(".//efac:InterestExpressionReceptionPeriod/cbc:EndTime/text()", namespaces=namespaces)
        
        if end_date:
            result[lot_id] = {
                "date": end_date[0],
                "time": end_time[0] if end_time else None
            }

    return result

def merge_lot_deadline_receipt_expressions(release_json, deadline_data):
    if deadline_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, data in deadline_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            tender_period = lot.setdefault("tenderPeriod", {})
            tender_period["endDate"] = combine_date_time(data["date"], data["time"])

    return release_json

def combine_date_time(date_str, time_str):
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    if time_str:
        time_obj = datetime.strptime(time_str, "%H:%M:%S%z")
        date_obj = date_obj.replace(hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second, tzinfo=time_obj.tzinfo)
    else:
        # If no time is provided, use 23:59:59 for end dates
        date_obj = date_obj.replace(hour=23, minute=59, second=59)
    
    # If no timezone is provided, assume UTC
    if date_obj.tzinfo is None:
        date_obj = date_obj.replace(tzinfo=datetime.timezone.utc)
    
    return date_obj.isoformat()