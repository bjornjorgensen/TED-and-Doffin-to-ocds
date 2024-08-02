# converters/BT_760_LotResult.py

import logging
from lxml import etree
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Mapping for received submission types
SUBMISSION_TYPE_MAPPING = {
    "part-req": "requests",
    "t-esubm": "electronicBids",
    "t-med": "mediumBids",
    "t-micro": "microBids",
    "t-no-eea": "foreignBidsFromNonEU",
    "t-oth-eea": "foreignBidsFromEU",
    "t-small": "smallBids",
    "t-sme": "smeBids",
    "t-verif-inad": "disqualifiedBids",
    "t-verif-inad-low": "tendersAbnormallyLow",
    "tenders": "bids"
}

def parse_received_submissions_type(xml_content: str) -> Optional[Dict]:
    """
    Parse the XML content to extract the received submissions type.

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
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1'
    }

    result = {"bids": {"statistics": []}}
    statistic_id = 1

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        received_submissions = lot_result.xpath("efac:ReceivedSubmissionsStatistics/efbc:StatisticsCode[@listName='received-submission-type']/text()", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if received_submissions and lot_id:
            for submission_type in received_submissions:
                if submission_type in SUBMISSION_TYPE_MAPPING:
                    statistic = {
                        "id": str(statistic_id),
                        "measure": SUBMISSION_TYPE_MAPPING[submission_type],
                        "relatedLot": lot_id[0]
                    }
                    result["bids"]["statistics"].append(statistic)
                    statistic_id += 1

    return result if result["bids"]["statistics"] else None

def merge_received_submissions_type(release_json: Dict, received_submissions_type_data: Optional[Dict]) -> None:
    """
    Merge the parsed received submissions type data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        received_submissions_type_data (Optional[Dict]): The parsed received submissions type data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not received_submissions_type_data:
        logger.warning("No received submissions type data to merge")
        return

    if "bids" not in release_json:
        release_json["bids"] = {}
    if "statistics" not in release_json["bids"]:
        release_json["bids"]["statistics"] = []

    for new_statistic in received_submissions_type_data["bids"]["statistics"]:
        existing_statistic = next((stat for stat in release_json["bids"]["statistics"] if stat.get("id") == new_statistic["id"]), None)
        
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            release_json["bids"]["statistics"].append(new_statistic)

    logger.info(f"Merged received submissions type data for {len(received_submissions_type_data['bids']['statistics'])} statistics")