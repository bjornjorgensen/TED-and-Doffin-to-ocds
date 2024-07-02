# converters/BT_125_Part.py

from lxml import etree
import logging, json

logger = logging.getLogger(__name__)

def parse_previous_planning_identifier_part(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"relatedProcesses": []}
    related_process_id = 1

    parts = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    logger.info(f"Found {len(parts)} parts")
    
    for part in parts:
        notice_refs = part.xpath("cac:TenderingProcess/cac:NoticeDocumentReference", namespaces=namespaces)
        logger.info(f"Found {len(notice_refs)} notice references for part")
        
        for notice_ref in notice_refs:
            identifier = notice_ref.xpath("cbc:ID[@schemeName='notice-id-ref']/text()", namespaces=namespaces)
            part_identifier = notice_ref.xpath("cbc:ReferencedDocumentInternalAddress/text()", namespaces=namespaces)
            
            logger.info(f"Identifier: {identifier}, Part Identifier: {part_identifier}")
            
            if identifier and part_identifier:
                full_identifier = f"{identifier[0]}-{part_identifier[0]}"
                related_process = {
                    "id": str(related_process_id),
                    "relationship": ["planning"],
                    "scheme": "eu-oj",
                    "identifier": full_identifier
                }
                result["relatedProcesses"].append(related_process)
                related_process_id += 1
                logger.info(f"Added related process for part: {related_process}")

    logger.info(f"Total related processes for parts: {len(result['relatedProcesses'])}")
    return result if result["relatedProcesses"] else None

def merge_previous_planning_identifier_part(release_json, previous_planning_data):
    if not previous_planning_data:
        logger.warning("No Previous Planning Identifier (Part) data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])
    
    for new_process in previous_planning_data["relatedProcesses"]:
        existing_process = next((p for p in existing_related_processes if p["id"] == new_process["id"]), None)
        if existing_process:
            existing_process.update(new_process)
        else:
            existing_related_processes.append(new_process)

    # Ensure the changes are reflected in the release_json object
    release_json["relatedProcesses"] = existing_related_processes

    logger.info(f"Merged Previous Planning Identifier (Part) data for {len(previous_planning_data['relatedProcesses'])} related processes")
    logger.info(f"Updated release_json: {json.dumps(release_json, indent=2)}")