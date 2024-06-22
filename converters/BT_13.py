from lxml import etree
from datetime import datetime, timezone

def parse_additional_info_deadline(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}
    lots = []

    # Parse for Lots
    lot_periods = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingProcess/cac:AdditionalInformationRequestPeriod", namespaces=namespaces)
    for period in lot_periods:
        lot_id = period.xpath("../../cbc:ID/text()", namespaces=namespaces)[0]
        end_date = period.xpath("cbc:EndDate/text()", namespaces=namespaces)
        end_time = period.xpath("cbc:EndTime/text()", namespaces=namespaces)
        
        if end_date:
            date_time = combine_date_time(end_date[0], end_time[0] if end_time else None)
            lots.append({
                "id": lot_id,
                "enquiryPeriod": {
                    "endDate": date_time
                }
            })

    if lots:
        result["tender"]["lots"] = lots

    # Parse for Parts
    part_period = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cac:AdditionalInformationRequestPeriod", namespaces=namespaces)
    if part_period:
        end_date = part_period[0].xpath("cbc:EndDate/text()", namespaces=namespaces)
        end_time = part_period[0].xpath("cbc:EndTime/text()", namespaces=namespaces)
        
        if end_date:
            date_time = combine_date_time(end_date[0], end_time[0] if end_time else None)
            result["tender"]["enquiryPeriod"] = {"endDate": date_time}

    return result if result["tender"] else None

def combine_date_time(date_str, time_str=None):
    date = datetime.fromisoformat(date_str)
    if time_str:
        time = datetime.strptime(time_str, "%H:%M:%S%z").time()
        date = date.replace(hour=time.hour, minute=time.minute, second=time.second, tzinfo=time.tzinfo)
    else:
        date = date.replace(hour=23, minute=59, second=59)
    
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)
    
    return date.isoformat()