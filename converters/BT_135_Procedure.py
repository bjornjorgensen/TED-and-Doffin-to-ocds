# converters/BT_135_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_direct_award_justification_rationale(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}
    
    xpath = "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/cbc:ProcessReason"
    reasons = root.xpath(xpath, namespaces=namespaces)
    
    if reasons:
        rationale = " ".join(reason.text for reason in reasons if reason.text)
        return {"tender": {"procurementMethodRationale": rationale}}
    
    logger.info("No direct award justification rationale found")
    return None

def merge_direct_award_justification_rationale(release_json, justification_data):
    if not justification_data:
        return
    
    tender = release_json.setdefault("tender", {})
    tender["procurementMethodRationale"] = justification_data["tender"]["procurementMethodRationale"]
    logger.info("Merged direct award justification rationale")