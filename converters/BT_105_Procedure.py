# converters/BT_105_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_procedure_type(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    procedure_code_mapping = {
        'open': 'open',
        'restricted': 'selective',
        'comp-dial': 'selective',
        'comp-tend': 'selective',
        'innovation': 'selective',
        'neg-w-call': 'selective',
        'neg-wo-call': 'limited',
        'exp-int-rail': 'selective',
        'oth-mult': None,
        'oth-single': None
    }

    procedure_details_mapping = {
        'comp-dial': 'Competitive dialogue',
        'comp-tend': 'Competitive tendering (article 5(3) of Regulation 1370/2007)',
        'exp-int-rail': 'Request for expression of interest – only for rail (article 5(3b) of Regulation 1370/2007)',
        'innovation': 'Innovation partnership',
        'neg-w-call': 'Negotiated with prior publication of a call for competition / competitive with negotiation',
        'neg-wo-call': 'Negotiated without prior call for competition',
        'open': 'Open',
        'oth-mult': 'Other multiple stage procedure',
        'oth-single': 'Other single stage procedure',
        'restricted': 'Restricted'
    }

    procedure_code = root.xpath("//cac:TenderingProcess/cbc:ProcedureCode[@listName='procurement-procedure-type']/text()", namespaces=namespaces)
    
    if procedure_code:
        procedure_code = procedure_code[0]
        if procedure_code in procedure_code_mapping:
            if procedure_code_mapping[procedure_code] is not None:
                result["tender"]["procurementMethod"] = procedure_code_mapping[procedure_code]
        
        if procedure_code in procedure_details_mapping:
            result["tender"]["procurementMethodDetails"] = procedure_details_mapping[procedure_code]

    return result if result["tender"] else None

def merge_procedure_type(release_json, procedure_type_data):
    if not procedure_type_data:
        logger.warning("No procedure type data to merge")
        return

    tender = release_json.setdefault("tender", {})
    
    if "procurementMethod" in procedure_type_data["tender"]:
        tender["procurementMethod"] = procedure_type_data["tender"]["procurementMethod"]
    
    if "procurementMethodDetails" in procedure_type_data["tender"]:
        tender["procurementMethodDetails"] = procedure_type_data["tender"]["procurementMethodDetails"]

    logger.info("Merged procedure type data")