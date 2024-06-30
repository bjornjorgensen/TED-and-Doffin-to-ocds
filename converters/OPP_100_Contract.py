# converters/OPP_100_Contract.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_framework_notice_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"contracts": []}

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for contract in settled_contracts:
        contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)[0]
        notice_references = contract.xpath("cac:NoticeDocumentReference", namespaces=namespaces)
        
        if notice_references:
            contract_data = {
                "id": contract_id,
                "relatedProcesses": []
            }
            
            for i, reference in enumerate(notice_references, start=1):
                scheme = reference.xpath("cbc:ID/@schemeName", namespaces=namespaces)
                identifier = reference.xpath("cbc:ID/text()", namespaces=namespaces)
                
                if scheme and identifier:
                    related_process = {
                        "id": str(i),
                        "scheme": scheme[0],
                        "identifier": identifier[0],
                        "relationship": ["framework"]
                    }
                    contract_data["relatedProcesses"].append(related_process)
            
            # Find the corresponding LotResult to get the awardID
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']", namespaces=namespaces)
            if lot_result:
                award_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
                if award_id:
                    contract_data["awardID"] = award_id[0]
            
            result["contracts"].append(contract_data)

    return result if result["contracts"] else None

def merge_framework_notice_identifier(release_json, framework_notice_data):
    if not framework_notice_data:
        logger.warning("No Framework Notice Identifier data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in framework_notice_data["contracts"]:
        existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
        if existing_contract:
            existing_related_processes = existing_contract.setdefault("relatedProcesses", [])
            for new_process in new_contract["relatedProcesses"]:
                if new_process not in existing_related_processes:
                    existing_related_processes.append(new_process)
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(f"Merged Framework Notice Identifier for {len(framework_notice_data['contracts'])} contracts")