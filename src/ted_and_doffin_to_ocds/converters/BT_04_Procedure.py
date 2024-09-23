# converters/BT_04_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    contract_folder_id_elements = root.xpath(
        "//cbc:ContractFolderID",
        namespaces=namespaces,
    )

    if contract_folder_id_elements:
        contract_folder_id = contract_folder_id_elements[0].text
        return {"tender": {"id": contract_folder_id}}
    logger.info("No Procedure Identifier found")
    return None


def merge_procedure_identifier(release_json, procedure_identifier_data):
    if not procedure_identifier_data:
        return

    tender = release_json.setdefault("tender", {})
    tender.update(procedure_identifier_data["tender"])
    logger.info("Merged Procedure Identifier data")
