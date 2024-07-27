# converters/BT_736_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_reserved_execution(xml_content):
    """
    Parse the XML content to extract the reserved execution information for each lot.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed reserved execution data for lots.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        reserved_execution = lot.xpath(".//cac:ContractExecutionRequirement/cbc:ExecutionRequirementCode[@listName='reserved-execution']/text()", namespaces=namespaces)
        
        if reserved_execution and reserved_execution[0].lower() == 'yes':
            lot_data = {
                "id": lot_id,
                "contractTerms": {
                    "reservedExecution": True
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_reserved_execution(release_json, reserved_execution_data):
    """
    Merge the parsed reserved execution data for lots into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        reserved_execution_data (dict): The parsed reserved execution data for lots to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not reserved_execution_data:
        logger.warning("No reserved execution data for lots to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    # Create a new list to store updated lots
    updated_lots = []

    for new_lot in reserved_execution_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(new_lot["contractTerms"])
            updated_lots.append(existing_lot)
        else:
            updated_lots.append(new_lot)

    # Replace the existing lots with the updated lots
    tender["lots"] = updated_lots

    logger.info(f"Merged reserved execution data for {len(updated_lots)} lots")