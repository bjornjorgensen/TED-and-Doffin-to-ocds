# converters/BT_195_BT_106_Procedure.py

from lxml import etree
import logging
from utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)

# Authority table for justification codes
JUSTIFICATION_CODES = {
    'eo-int': {
        'description': 'Commercial interests of an economic operator',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/eo-int'
    },
    'fair-comp': {
        'description': 'Fair competition',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/fair-comp'
    },
    'law-enf': {
        'description': 'Law enforcement',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/law-enf'
    },
    'oth-int': {
        'description': 'Other public interest',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/oth-int'
    },
    'rd-ser': {
        'description': 'Research and development (R&D) services',
        'uri': 'http://publications.europa.eu/resource/authority/non-publication-justification/rd-ser'
    }
}

def parse_unpublished_procedure_accelerated(xml_content):
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

    fields_privacy = root.xpath("//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc']", namespaces=namespaces)
    
    for field_privacy in fields_privacy:
        field_identifier_code = field_privacy.xpath("efbc:FieldIdentifierCode/text()", namespaces=namespaces)
        reason_description = field_privacy.xpath("efbc:ReasonDescription/text()", namespaces=namespaces)
        reason_code = field_privacy.xpath("cbc:ReasonCode/text()", namespaces=namespaces)
        publication_date = field_privacy.xpath("efbc:PublicationDate/text()", namespaces=namespaces)
        
        if field_identifier_code:
            withheld_info = {
                "id": f"{field_identifier_code[0]}-{contract_folder_id[0]}",
                "field": field_identifier_code[0],
                "name": "Procedure Accelerated"
            }
            if reason_description:
                withheld_info["rationale"] = reason_description[0]
            
            if reason_code:
                code = reason_code[0]
                if code in JUSTIFICATION_CODES:
                    withheld_info["rationaleClassifications"] = [{
                        "scheme": "eu-non-publication-justification",
                        "id": code,
                        "description": JUSTIFICATION_CODES[code]['description'],
                        "uri": JUSTIFICATION_CODES[code]['uri']
                    }]
            
            if publication_date:
                withheld_info["availabilityDate"] = convert_to_iso_format(publication_date[0])
            
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def merge_unpublished_procedure_accelerated(release_json, unpublished_procedure_accelerated_data):
    if not unpublished_procedure_accelerated_data:
        logger.warning("No Unpublished Procedure Accelerated data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_withheld_info in unpublished_procedure_accelerated_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_withheld_info["id"]), None)
        if existing_item:
            existing_item.update(new_withheld_info)
        else:
            existing_withheld_info.append(new_withheld_info)

    logger.info(f"Merged Unpublished Procedure Accelerated data for {len(unpublished_procedure_accelerated_data['withheldInformation'])} items")