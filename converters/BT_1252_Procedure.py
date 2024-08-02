# converters/BT_1252_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_direct_award_justification(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"relatedProcesses": []}
    process_justifications = root.xpath("//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']", namespaces=namespaces)

    for justification in process_justifications:
        identifier = justification.xpath("cbc:Description/text()", namespaces=namespaces)
        reason_code = justification.xpath("cbc:ProcessReasonCode/text()", namespaces=namespaces)

        if identifier:
            related_process = {
                "identifier": identifier[0],
                "scheme": "eu-oj",
                "relationship": []
            }

            if reason_code:
                if reason_code[0] in ["irregular", "unsuitable"]:
                    related_process["relationship"].append("unsuccessfulProcess")
                elif reason_code[0] in ["additional", "existing", "repetition"]:
                    related_process["relationship"].append("prior")

            result["relatedProcesses"].append(related_process)

    return result if result["relatedProcesses"] else None

def merge_direct_award_justification(release_json, direct_award_data):
    if not direct_award_data:
        logger.warning("No Direct Award Justification data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])
    
    # Find the highest existing id
    max_id = max([int(p["id"]) for p in existing_related_processes]) if existing_related_processes else 0
    
    for new_process in direct_award_data["relatedProcesses"]:
        max_id += 1
        new_process["id"] = str(max_id)
        existing_related_processes.append(new_process)

    logger.info(f"Merged Direct Award Justification data for {len(direct_award_data['relatedProcesses'])} related processes")