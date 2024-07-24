# converters/BT_04_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_procedure_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    contract_folder_id_elements = root.xpath("//cbc:ContractFolderID", namespaces=namespaces)

    if contract_folder_id_elements:
        contract_folder_id = contract_folder_id_elements[0].text
        return {
            "tender": {
                "id": contract_folder_id
            }
        }
    else:
        logger.info("No Procedure Identifier found")
        return None

def merge_procedure_identifier(release_json, procedure_identifier_data):
    if not procedure_identifier_data:
        return

    tender = release_json.setdefault("tender", {})
    tender.update(procedure_identifier_data["tender"])
    logger.info("Merged Procedure Identifier data")