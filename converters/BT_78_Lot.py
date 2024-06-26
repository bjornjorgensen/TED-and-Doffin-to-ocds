# converters/BT_78_Lot.py

from lxml import etree
from datetime import datetime, timezone

def parse_security_clearance_deadline(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        deadline = lot.xpath("cac:TenderingTerms/cbc:LatestSecurityClearanceDate/text()", namespaces=namespaces)
        
        if deadline:
            result[lot_id] = deadline[0]

    return result

def format_date(date_string):
    try:
        # Try to parse the date with timezone
        dt = datetime.fromisoformat(date_string)
    except ValueError:
        # If parsing fails, assume it's a date without time
        dt = datetime.fromisoformat(date_string + 'T23:59:59')
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Format the datetime to ISO 8601 format
    return dt.isoformat()

def merge_security_clearance_deadline(release_json, security_clearance_data):
    if not security_clearance_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, deadline in security_clearance_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        milestones = lot.setdefault("milestones", [])
        milestone_id = str(len(milestones) + 1)
        
        milestones.append({
            "id": milestone_id,
            "type": "securityClearanceDeadline",
            "dueDate": format_date(deadline)
        })

    return release_json