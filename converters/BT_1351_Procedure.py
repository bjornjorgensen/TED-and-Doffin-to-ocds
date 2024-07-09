# converters/BT_1351_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_accelerated_procedure_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    justification = root.xpath("//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReason/text()", namespaces=namespaces)
    
    if justification:
        return {
            "tender": {
                "procedure": {
                    "acceleratedRationale": justification[0]
                }
            }
        }
    else:
        logger.info("No Accelerated Procedure Justification found")
        return None

def merge_accelerated_procedure_justification(release_json, accelerated_procedure_justification_data):
    if not accelerated_procedure_justification_data:
        logger.warning("No Accelerated Procedure Justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    procedure = tender.setdefault("procedure", {})
    procedure["acceleratedRationale"] = accelerated_procedure_justification_data["tender"]["procedure"]["acceleratedRationale"]

    logger.info(f"Merged Accelerated Procedure Justification data: {procedure['acceleratedRationale']}")
    logger.debug(f"Release JSON after merging Accelerated Procedure Justification data: {release_json}")