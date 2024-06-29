# converters/OPP_090_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_previous_notice_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"relatedProcesses": []}
    notice_refs = root.xpath("//cac:TenderingProcess/cac:NoticeDocumentReference/cbc:ID[@schemeName='notice-id-ref']", namespaces=namespaces)

    for index, notice_ref in enumerate(notice_refs, start=1):
        result["relatedProcesses"].append({
            "id": str(index),
            "relationship": ["planning"],
            "scheme": "eu-oj",
            "identifier": notice_ref.text
        })

    return result if result["relatedProcesses"] else None

def merge_previous_notice_identifier(release_json, previous_notice_data):
    if not previous_notice_data:
        logger.warning("No Previous Notice Identifier data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])
    
    for new_process in previous_notice_data["relatedProcesses"]:
        existing_process = next((p for p in existing_related_processes if p["id"] == new_process["id"]), None)
        if existing_process:
            existing_process.update(new_process)
        else:
            existing_related_processes.append(new_process)

    logger.info(f"Merged Previous Notice Identifier for {len(previous_notice_data['relatedProcesses'])} related processes")