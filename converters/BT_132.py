from lxml import etree
from datetime import datetime, timezone

def parse_public_opening_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        occurrence_date = lot.xpath("cac:TenderingProcess/cac:OpenTenderEvent/cbc:OccurrenceDate/text()", namespaces=namespaces)
        occurrence_time = lot.xpath("cac:TenderingProcess/cac:OpenTenderEvent/cbc:OccurrenceTime/text()", namespaces=namespaces)
        
        if occurrence_date:
            formatted_date = format_date(occurrence_date[0], occurrence_time[0] if occurrence_time else None)
            lot_data = {
                "id": lot_id,
                "awardPeriod": {
                    "startDate": formatted_date
                },
                "bidOpening": {
                    "date": formatted_date
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def format_date(date_str, time_str=None):
    date = datetime.fromisoformat(date_str)
    if time_str:
        time = datetime.strptime(time_str, "%H:%M:%S%z").time()
        date = date.replace(hour=time.hour, minute=time.minute, second=time.second, tzinfo=time.tzinfo)
    else:
        date = date.replace(hour=0, minute=0, second=0)
    
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    
    return date.isoformat()