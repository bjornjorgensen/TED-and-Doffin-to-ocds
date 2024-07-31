# converters/BT_195_BT_1351_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_procedure_accelerated_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"withheldInformation": []}

    contract_folder_id = root.xpath("//cbc:ContractFolderID/text()", namespaces=namespaces)
    if not contract_folder_id:
        logger.warning("No ContractFolderID found")
        return None

    field_identifier_codes = root.xpath("//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc-jus']/efbc:FieldIdentifierCode/text()", namespaces=namespaces)
    
    for field_identifier_code in field_identifier_codes:
        withheld_info = {
            "id": f"{field_identifier_code}-{contract_folder_id[0]}",
            "field": field_identifier_code,
            "name": "Procedure Accelerated Justification"
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def merge_unpublished_procedure_accelerated_justification(release_json, unpublished_procedure_accelerated_justification_data):
    if not unpublished_procedure_accelerated_justification_data:
        logger.warning("No Unpublished Procedure Accelerated Justification data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_withheld_info in unpublished_procedure_accelerated_justification_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_withheld_info["id"]), None)
        if existing_item:
            existing_item.update(new_withheld_info)
        else:
            existing_withheld_info.append(new_withheld_info)

    logger.info(f"Merged Unpublished Procedure Accelerated Justification data for {len(unpublished_procedure_accelerated_justification_data['withheldInformation'])} items")