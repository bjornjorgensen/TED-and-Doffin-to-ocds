# converters/BT_531_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_procedure_additional_nature(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"additionalProcurementCategories": []}}

    additional_natures = root.xpath("//cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='contract-nature']/cbc:ProcurementTypeCode/text()", namespaces=namespaces)
    
    if additional_natures:
        result["tender"]["additionalProcurementCategories"] = list(set(additional_natures))  # Remove duplicates

    return result if result["tender"]["additionalProcurementCategories"] else None

def merge_procedure_additional_nature(release_json, procedure_additional_nature_data):
    if not procedure_additional_nature_data:
        logger.warning("No Procedure Additional Nature data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_categories = set(tender.get("additionalProcurementCategories", []))
    new_categories = set(procedure_additional_nature_data["tender"]["additionalProcurementCategories"])
    
    combined_categories = list(existing_categories.union(new_categories))
    tender["additionalProcurementCategories"] = combined_categories

    logger.info(f"Merged Procedure Additional Nature data: {len(combined_categories)} categories")