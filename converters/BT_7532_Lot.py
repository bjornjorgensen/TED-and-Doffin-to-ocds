# converters/BT_7532_Lot.py

import logging
from lxml import etree
from typing import Dict, Union, List, Optional

logger = logging.getLogger(__name__)

def parse_selection_criteria_number_threshold(xml_content: Union[str, bytes]) -> Optional[Dict]:
    """
    Parse the XML content to extract the selection criteria number threshold information.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data, or None if no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    threshold_mapping: Dict[str, str] = {
        'min-score': 'minimumScore',
        'max-bids': 'maximumBids'
    }

    result: Dict[str, Dict[str, List[Dict]]] = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id: str = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//efac:SelectionCriteria[cbc:CalculationExpressionCode[@listName='usage'] = 'used']", namespaces=namespaces)
        
        lot_data: Dict[str, Union[str, Dict[str, List]]] = {
            "id": lot_id,
            "selectionCriteria": {
                "criteria": []
            }
        }

        for criterion in criteria:
            criterion_data: Dict[str, List] = {"numbers": []}
            parameters = criterion.xpath(".//efac:CriterionParameter[efbc:ParameterCode/@listName='number-threshold']", namespaces=namespaces)
            
            for parameter in parameters:
                threshold_code: str = parameter.xpath("efbc:ParameterCode/text()", namespaces=namespaces)[0]
                threshold_value: Optional[str] = threshold_mapping.get(threshold_code)
                
                if threshold_value:
                    criterion_data["numbers"].append({"threshold": threshold_value})
            
            if criterion_data["numbers"]:
                lot_data["selectionCriteria"]["criteria"].append(criterion_data)

        if lot_data["selectionCriteria"]["criteria"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_selection_criteria_number_threshold(release_json: Dict, parsed_data: Optional[Dict]) -> None:
    """
    Merge the parsed selection criteria number threshold data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        parsed_data (Optional[Dict]): The parsed selection criteria number threshold data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not parsed_data:
        logger.warning("No Selection Criteria Number Threshold data to merge")
        return

    tender_lots: List[Dict] = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in parsed_data["tender"]["lots"]:
        existing_lot = next((lot for lot in tender_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_criteria = existing_lot.setdefault("selectionCriteria", {}).setdefault("criteria", [])
            for new_criterion in new_lot["selectionCriteria"]["criteria"]:
                existing_criterion = next((c for c in existing_criteria if c.get("id") == new_criterion.get("id")), None)
                if existing_criterion:
                    existing_numbers = existing_criterion.setdefault("numbers", [])
                    for new_number in new_criterion["numbers"]:
                        existing_number = next((n for n in existing_numbers if n.get("id") == new_number.get("id")), None)
                        if existing_number:
                            existing_number.update(new_number)
                        else:
                            existing_numbers.append(new_number)
                else:
                    existing_criteria.append(new_criterion)
        else:
            tender_lots.append(new_lot)

    logger.info(f"Merged Selection Criteria Number Threshold data for {len(parsed_data['tender']['lots'])} lots")