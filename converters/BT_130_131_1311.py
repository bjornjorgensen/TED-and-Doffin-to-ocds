from lxml import etree
from datetime import datetime, timezone

def parse_tender_deadlines_invitations(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    procurement_project_lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        lot_data = {"id": lot_id}

        # BT-130: Dispatch Invitation Tender
        invitation_date = lot.xpath("cac:TenderingProcess/cac:InvitationSubmissionPeriod/cbc:StartDate/text()", namespaces=namespaces)
        if invitation_date:
            lot_data["secondStage"] = {
                "invitationDate": format_date(invitation_date[0])
            }

        # BT-131: Deadline Receipt Tenders
        tender_end_date = lot.xpath("cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndDate/text()", namespaces=namespaces)
        tender_end_time = lot.xpath("cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndTime/text()", namespaces=namespaces)
        if tender_end_date:
            lot_data["tenderPeriod"] = {
                "endDate": format_date(tender_end_date[0], tender_end_time[0] if tender_end_time else None)
            }

        # BT-1311: Deadline Receipt Requests
        request_end_date = lot.xpath("cac:TenderingProcess/cac:ParticipationRequestReceptionPeriod/cbc:EndDate/text()", namespaces=namespaces)
        request_end_time = lot.xpath("cac:TenderingProcess/cac:ParticipationRequestReceptionPeriod/cbc:EndTime/text()", namespaces=namespaces)
        if request_end_date:
            if "tenderPeriod" not in lot_data:
                lot_data["tenderPeriod"] = {}
            lot_data["tenderPeriod"]["endDate"] = format_date(request_end_date[0], request_end_time[0] if request_end_time else None)

        if len(lot_data) > 1:  # Only add if there's more than just the ID
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