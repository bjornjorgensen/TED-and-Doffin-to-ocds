# converters/BT_125_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_previous_planning_identifier_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"relatedProcesses": []}
    related_process_id = 1

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        notice_refs = lot.xpath("cac:TenderingProcess/cac:NoticeDocumentReference/cbc:ID[@schemeName='notice-id-ref']/text()", namespaces=namespaces)
        
        for identifier in notice_refs:
            related_process = {
                "id": str(related_process_id),
                "relationship": ["planning"],
                "scheme": "eu-oj",
                "identifier": identifier
            }
            result["relatedProcesses"].append(related_process)
            related_process_id += 1

    return result if result["relatedProcesses"] else None

def merge_previous_planning_identifier_lot(release_json, previous_planning_data):
    if not previous_planning_data:
        logger.warning("No Previous Planning Identifier (Lot) data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])
    
    for new_process in previous_planning_data["relatedProcesses"]:
        existing_process = next((p for p in existing_related_processes if p["identifier"] == new_process["identifier"]), None)
        if existing_process:
            existing_process.update(new_process)
        else:
            existing_related_processes.append(new_process)

    logger.info(f"Merged Previous Planning Identifier (Lot) data for {len(previous_planning_data['relatedProcesses'])} related processes")