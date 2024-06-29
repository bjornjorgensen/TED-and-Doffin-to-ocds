# converters/BT_88_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_procedure_features(xml_content):
    logger.info("Parsing BT-88-Procedure: Procedure Features")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    procedure_features = root.xpath("//cac:TenderingProcess/cbc:Description/text()", namespaces=namespaces)
    
    if procedure_features:
        logger.debug(f"Found Procedure Features: {procedure_features[0]}")
        result["tender"]["procurementMethodDetails"] = procedure_features[0]
    else:
        logger.debug("No Procedure Features found")

    return result

def merge_procedure_features(release_json, procedure_features_data):
    logger.info("Merging BT-88-Procedure: Procedure Features")
    if "tender" not in procedure_features_data or "procurementMethodDetails" not in procedure_features_data["tender"]:
        logger.warning("No Procedure Features data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender["procurementMethodDetails"] = procedure_features_data["tender"]["procurementMethodDetails"]
    logger.debug("Merged Procedure Features")