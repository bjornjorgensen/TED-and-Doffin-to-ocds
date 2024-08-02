# converters/BT_710_LotResult.py

import logging
from lxml import etree
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def parse_tender_value_lowest(xml_content: str) -> Optional[Dict]:
    """
    Parse the XML content to extract the lowest tender value.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data if found, None otherwise.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1'
    }

    result = {"bids": {"statistics": []}}
    statistic_id = 1

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lower_tender_amount = lot_result.xpath("cbc:LowerTenderAmount", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if lower_tender_amount and lot_id:
            statistic = {
                "id": str(statistic_id),
                "measure": "lowestValidBidValue",
                "value": float(lower_tender_amount[0].text),
                "currency": lower_tender_amount[0].get("currencyID"),
                "relatedLot": lot_id[0]
            }
            result["bids"]["statistics"].append(statistic)
            statistic_id += 1

    return result if result["bids"]["statistics"] else None

def merge_tender_value_lowest(release_json: Dict, tender_value_lowest_data: Optional[Dict]) -> None:
    """
    Merge the parsed lowest tender value data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        tender_value_lowest_data (Optional[Dict]): The parsed lowest tender value data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not tender_value_lowest_data:
        logger.warning("No lowest tender value data to merge")
        return

    if "bids" not in release_json:
        release_json["bids"] = {}
    
    if "statistics" not in release_json["bids"]:
        release_json["bids"]["statistics"] = []

    for new_statistic in tender_value_lowest_data["bids"]["statistics"]:
        existing_statistic = next((stat for stat in release_json["bids"]["statistics"] if stat.get("id") == new_statistic["id"]), None)
        
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            release_json["bids"]["statistics"].append(new_statistic)

    logger.info(f"Merged lowest tender value data for {len(tender_value_lowest_data['bids']['statistics'])} statistics")