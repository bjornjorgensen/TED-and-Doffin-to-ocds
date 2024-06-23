# converters/BT_631_Lot_Dispatch_Invitation_Interest.py
from lxml import etree
from datetime import datetime, timezone

def parse_lot_dispatch_invitation_interest(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        start_date = lot.xpath("cac:TenderingProcess/cac:ParticipationInvitationPeriod/cbc:StartDate/text()", namespaces=namespaces)
        
        if start_date:
            result[lot_id] = start_date[0]

    return result

def merge_lot_dispatch_invitation_interest(release_json, dispatch_data):
    if dispatch_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, start_date in dispatch_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            communication = lot.setdefault("communication", {})
            communication["invitationToConfirmInterestDispatchDate"] = convert_to_iso_format(start_date)

    return release_json

def convert_to_iso_format(date_str):
    try:
        # Parse the date string
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        # If no time component, set it to 00:00:00
        if date_obj.hour == 0 and date_obj.minute == 0 and date_obj.second == 0:
            date_obj = date_obj.replace(hour=0, minute=0, second=0)
        
        # If no timezone, assume UTC
        if date_obj.tzinfo is None:
            date_obj = date_obj.replace(tzinfo=timezone.utc)
        
        # Convert to ISO format
        return date_obj.isoformat()
    except ValueError:
        # If parsing fails, return the original string
        return date_str