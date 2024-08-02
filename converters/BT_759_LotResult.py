# converters/BT_759_LotResult.py

import logging
from lxml import etree
from typing import Dict, Union, Optional, List

logger = logging.getLogger(__name__)

def parse_received_submissions_count(xml_content: Union[str, bytes]) -> Optional[Dict]:
    """
    Parse the XML content to extract the received submissions count for each lot.

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
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result: Dict[str, Dict[str, List[Dict]]] = {"bids": {"statistics": []}}
    
    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        if not lot_id:
            continue
        
        lot_id = lot_id[0]
        
        statistics = lot_result.xpath("efac:ReceivedSubmissionsStatistics/efbc:StatisticsNumeric/text()", namespaces=namespaces)
        if statistics:
            statistic = {
                "id": str(len(result["bids"]["statistics"]) + 1),
                "value": int(statistics[0]),
                "relatedLot": lot_id
            }
            result["bids"]["statistics"].append(statistic)

    return result if result["bids"]["statistics"] else None

def merge_received_submissions_count(release_json: Dict, parsed_data: Optional[Dict]) -> None:
    """
    Merge the parsed received submissions count data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        parsed_data (Optional[Dict]): The parsed received submissions count data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not parsed_data:
        logger.info("No Received Submissions Count data to merge")
        return

    bids = release_json.setdefault("bids", {})
    existing_statistics = bids.setdefault("statistics", [])

    for new_statistic in parsed_data["bids"]["statistics"]:
        existing_statistic = next((s for s in existing_statistics if s["relatedLot"] == new_statistic["relatedLot"]), None)
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(f"Merged Received Submissions Count data for {len(parsed_data['bids']['statistics'])} lots")