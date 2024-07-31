# converters/BT_805_Lot.py

from typing import Optional, Dict, Any, List
from lxml import etree

GPP_CRITERIA_MAPPING = {
    "eu": "euGPPCriteria",
    "national": "nationalGPPCriteria",
    "other": "otherGPPCriteria"
}

def parse_green_procurement_criteria(xml_content: str) -> Optional[Dict[str, Any]]:
    """
    Parse the XML content to extract the Green Procurement Criteria for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the parsed data if found, None otherwise.
    """
    root = etree.fromstring(xml_content.encode('utf-8'))
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result: Dict[str, Any] = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        gpp_criteria = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='gpp-criteria']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces
        )

        if gpp_criteria and "none" not in gpp_criteria:
            sustainability: List[Dict[str, List[str]]] = []
            for criterion in gpp_criteria:
                if criterion in GPP_CRITERIA_MAPPING:
                    sustainability.append({"strategies": [GPP_CRITERIA_MAPPING[criterion]]})

            if sustainability:
                result["tender"]["lots"].append({
                    "id": lot_id,
                    "hasSustainability": True,
                    "sustainability": sustainability
                })

    return result if result["tender"]["lots"] else None

def merge_green_procurement_criteria(release_json: Dict[str, Any], gpp_data: Optional[Dict[str, Any]]) -> None:
    """
    Merge the parsed Green Procurement Criteria data into the main OCDS release JSON.

    Args:
        release_json (Dict[str, Any]): The main OCDS release JSON to be updated.
        gpp_data (Optional[Dict[str, Any]]): The parsed Green Procurement Criteria data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not gpp_data:
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for gpp_lot in gpp_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == gpp_lot["id"]), None)
        if existing_lot:
            existing_lot["hasSustainability"] = gpp_lot["hasSustainability"]
            existing_lot["sustainability"] = gpp_lot["sustainability"]
        else:
            lots.append(gpp_lot)