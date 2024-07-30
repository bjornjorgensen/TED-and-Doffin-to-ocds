# converters/BT_88_Procedure.py

from typing import Optional, Dict, Any
from lxml import etree

def parse_procedure_features(xml_content: str) -> Optional[Dict[str, Any]]:
    """
    Parse the XML content to extract the Procedure Features.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the parsed data if found, None otherwise.
    """
    root = etree.fromstring(xml_content.encode('utf-8'))
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    procedure_features = root.xpath("//cac:TenderingProcess/cbc:Description/text()", namespaces=namespaces)

    if procedure_features:
        return {
            "tender": {
                "procurementMethodDetails": procedure_features[0].strip()
            }
        }

    return None

def merge_procedure_features(release_json: Dict[str, Any], procedure_features_data: Optional[Dict[str, Any]]) -> None:
    """
    Merge the parsed Procedure Features data into the main OCDS release JSON.

    Args:
        release_json (Dict[str, Any]): The main OCDS release JSON to be updated.
        procedure_features_data (Optional[Dict[str, Any]]): The parsed Procedure Features data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not procedure_features_data:
        return

    tender = release_json.setdefault("tender", {})
    tender["procurementMethodDetails"] = procedure_features_data["tender"]["procurementMethodDetails"]