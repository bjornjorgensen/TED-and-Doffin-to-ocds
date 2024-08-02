# converters/BT_760_LotResult.py

import logging
from lxml import etree
from typing import Dict, Union, Optional, List

logger = logging.getLogger(__name__)

def parse_received_submissions_type(xml_content: Union[str, bytes]) -> Optional[Dict]:
    """
    Parse the XML content to extract the received submissions type for each lot.

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
    
    submission_type_mapping = {
        'part-req': 'requests',
        't-esubm': 'electronicBids',
        't-med': 'mediumBids',
        't-micro': 'microBids',
        't-no-eea': 'foreignBidsFromNonEU',
        't-no-verif': '',
        't-oth-eea': 'foreignBidsFromEU',
        't-small': 'smallBids',
        't-sme': 'smeBids',
        't-verif-inad': 'disqualifiedBids',
        't-verif-inad-low': 'tendersAbnormallyLow',
        'tenders': 'bids'
    }

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    logger.info(f"Found {len(lot_results)} LotResult elements")
    
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        if not lot_id:
            logger.warning("LotResult found without a lot ID")
            continue
        
        lot_id = lot_id[0]
        logger.info(f"Processing lot ID: {lot_id}")
        
        statistics = lot_result.xpath("efac:ReceivedSubmissionsStatistics/efbc:StatisticsCode[@listName='received-submission-type']/text()", namespaces=namespaces)
        logger.info(f"Found {len(statistics)} statistics for lot {lot_id}")
        
        for stat_code in statistics:
            if stat_code in submission_type_mapping:
                measure = submission_type_mapping[stat_code]
                if measure:  # Skip empty measures
                    statistic = {
                        "id": str(len(result["bids"]["statistics"]) + 1),
                        "measure": measure,
                        "relatedLot": lot_id
                    }
                    result["bids"]["statistics"].append(statistic)
                    logger.info(f"Added statistic: {statistic}")
            else:
                logger.warning(f"Unknown statistic code: {stat_code}")

    logger.info(f"Total statistics parsed: {len(result['bids']['statistics'])}")
    return result if result["bids"]["statistics"] else None

def merge_received_submissions_type(release_json: Dict, parsed_data: Optional[Dict]) -> None:
    """
    Merge the parsed received submissions type data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        parsed_data (Optional[Dict]): The parsed received submissions type data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not parsed_data:
        logger.info("No Received Submissions Type data to merge")
        return

    bids = release_json.setdefault("bids", {})
    existing_statistics = bids.setdefault("statistics", [])

    for new_statistic in parsed_data["bids"]["statistics"]:
        existing_statistic = next((s for s in existing_statistics 
                                   if s.get("relatedLot") == new_statistic["relatedLot"] 
                                   and s.get("measure") == new_statistic["measure"]), None)
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(f"Merged Received Submissions Type data for {len(parsed_data['bids']['statistics'])} statistics")