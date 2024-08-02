# converters/BT_712a_LotResult.py

import logging
from lxml import etree
from typing import Dict, Optional

logger = logging.getLogger(__name__)

def parse_buyer_review_complainants_code(xml_content: str) -> Optional[Dict]:
    """
    Parse the XML content to extract the buyer review complainants code.

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
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"statistics": []}
    statistic_id = 1

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        appeal_requests = lot_result.xpath("efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if appeal_requests and lot_id:
            stats_code = appeal_requests[0].xpath("efbc:StatisticsCode/text()", namespaces=namespaces)
            if stats_code and stats_code[0] == 'complainants':
                statistic = {
                    "id": str(statistic_id),
                    "measure": "complainants",
                    "relatedLot": lot_id[0]
                }
                result["statistics"].append(statistic)
                statistic_id += 1

    return result if result["statistics"] else None

def merge_buyer_review_complainants_code(release_json: Dict, buyer_review_complainants_code_data: Optional[Dict]) -> None:
    """
    Merge the parsed buyer review complainants code data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        buyer_review_complainants_code_data (Optional[Dict]): The parsed buyer review complainants code data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not buyer_review_complainants_code_data:
        logger.warning("No buyer review complainants code data to merge")
        return

    release_statistics = release_json.setdefault("statistics", [])
    
    for new_statistic in buyer_review_complainants_code_data["statistics"]:
        existing_statistic = next((stat for stat in release_statistics if stat.get("id") == new_statistic["id"]), None)
        
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            release_statistics.append(new_statistic)

    logger.info(f"Merged buyer review complainants code data for {len(buyer_review_complainants_code_data['statistics'])} statistics")