# converters/BT_635_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_buyer_review_requests_count(xml_content):
    """
    Parse the XML content to extract Buyer Review Requests Count data for each lot result.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "statistics": [
                      {
                          "id": "unique_id",
                          "value": int_value,
                          "scope": "complaints",
                          "relatedLot": "lot_id"
                      }
                  ]
              }
        None: If no relevant data is found.
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
    stat_id = 1

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        requests_count = lot_result.xpath("efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efbc:StatisticsNumeric/text()", namespaces=namespaces)
        
        if lot_id and requests_count:
            statistic = {
                "id": str(stat_id),
                "value": int(requests_count[0]),
                "scope": "complaints",
                "relatedLot": lot_id[0]
            }
            result["statistics"].append(statistic)
            stat_id += 1

    return result if result["statistics"] else None

def merge_buyer_review_requests_count(release_json, buyer_review_requests_data):
    """
    Merge the parsed Buyer Review Requests Count data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        buyer_review_requests_data (dict): The parsed Buyer Review Requests Count data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not buyer_review_requests_data:
        logger.warning("No Buyer Review Requests Count data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])
    
    for new_statistic in buyer_review_requests_data["statistics"]:
        existing_statistic = next((stat for stat in existing_statistics if stat["id"] == new_statistic["id"]), None)
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)
    
    logger.info(f"Merged Buyer Review Requests Count data for {len(buyer_review_requests_data['statistics'])} statistics")