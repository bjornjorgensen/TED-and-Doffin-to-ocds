# converters/BT_106_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_procedure_accelerated(xml_content):
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

    result = {"tender": {}}

    accelerated_code = root.xpath("//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReasonCode/text()", namespaces=namespaces)
    
    if accelerated_code:
        is_accelerated = accelerated_code[0].lower() == 'true'
        result["tender"]["procedure"] = {"isAccelerated": is_accelerated}

    return result

def merge_procedure_accelerated(release_json, procedure_accelerated_data):
    if not procedure_accelerated_data:
        logger.warning("No procedure accelerated data to merge")
        return

    tender = release_json.setdefault("tender", {})
    
    if "procedure" in procedure_accelerated_data["tender"]:
        procedure = tender.setdefault("procedure", {})
        procedure["isAccelerated"] = procedure_accelerated_data["tender"]["procedure"]["isAccelerated"]

    logger.info("Merged procedure accelerated data")