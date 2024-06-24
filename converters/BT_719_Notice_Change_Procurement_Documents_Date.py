# converters/BT_719_Notice_Change_Procurement_Documents_Date.py
from lxml import etree
from datetime import datetime, timezone

def parse_change_procurement_documents_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = []

    changes = root.xpath("//efac:Changes/efac:Change", namespaces=namespaces)
    for change in changes:
        change_date = change.xpath("efbc:ProcurementDocumentsChangeDate/text()", namespaces=namespaces)
        lot_identifiers = change.xpath("efac:ChangedSection/efbc:ChangedSectionIdentifier[starts-with(text(), 'LOT-')]/text()", namespaces=namespaces)
        
        if change_date:
            formatted_date = format_date(change_date[0])
            if lot_identifiers:
                for lot_id in lot_identifiers:
                    result.append({
                        "date": formatted_date,
                        "relatedLots": [lot_id]
                    })
            else:
                result.append({
                    "date": formatted_date,
                    "relatedLots": []
                })

    return result

def format_date(date_string):
    date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    
    if date_obj.hour == 0 and date_obj.minute == 0 and date_obj.second == 0:
        date_obj = date_obj.replace(hour=0, minute=0, second=0)
    else:
        date_obj = date_obj.replace(hour=23, minute=59, second=59)
    
    if date_obj.tzinfo is None:
        date_obj = date_obj.replace(tzinfo=timezone.utc)
    
    return date_obj.isoformat()

def merge_change_procurement_documents_date(release_json, change_data):
    if change_data:
        tender = release_json.setdefault("tender", {})
        documents = tender.setdefault("documents", [])

        for change in change_data:
            if change["relatedLots"]:
                for lot_id in change["relatedLots"]:
                    doc = next((d for d in documents if "biddingDocuments" in d.get("documentType", []) and lot_id in d.get("relatedLots", [])), None)
                    if doc:
                        doc["dateModified"] = change["date"]
            else:
                for doc in documents:
                    if "biddingDocuments" in doc.get("documentType", []):
                        doc["dateModified"] = change["date"]

    return release_json