# converters/BT_736_Reserved_Execution.py
from lxml import etree

def parse_reserved_execution(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {
        'lots': {},
        'part': False
    }

    # Process Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        execution_code = lot.xpath(".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='reserved-execution']/cbc:ExecutionRequirementCode/text()", namespaces=namespaces)
        if execution_code and execution_code[0].lower() == 'yes':
            result['lots'][lot_id] = True

    # Process Part
    part_execution_code = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='reserved-execution']/cbc:ExecutionRequirementCode/text()", namespaces=namespaces)
    if part_execution_code and part_execution_code[0].lower() == 'yes':
        result['part'] = True

    return result

def merge_reserved_execution(release_json, reserved_execution_data):
    if reserved_execution_data:
        tender = release_json.setdefault("tender", {})

        # Merge Lots
        lots = tender.setdefault("lots", [])
        for lot_id, reserved in reserved_execution_data['lots'].items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            contract_terms = lot.setdefault("contractTerms", {})
            contract_terms["reservedExecution"] = reserved

        # Merge Part
        if reserved_execution_data['part']:
            contract_terms = tender.setdefault("contractTerms", {})
            contract_terms["reservedExecution"] = True

    return release_json