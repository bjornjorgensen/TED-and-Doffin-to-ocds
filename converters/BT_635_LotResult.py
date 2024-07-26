# converters/BT_635_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_buyer_review_requests_count(xml_content):
    """
    Parse the XML content to extract the buyer review requests count for each lot result.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed buyer review requests count data in the format:
              {
                  "statistics": [
                      {
                          "id": "1",
                          "value": 2,
                          "scope": "complaints",
                          "relatedLot": "LOT-0001"
                      }
                  ]
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"statistics": []}
    statistic_id = 1

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        statistics_numeric = lot_result.xpath("efac:AppealRequestsStatistics/efbc:StatisticsNumeric/text()", namespaces=namespaces)
        
        if lot_id and statistics_numeric:
            statistic = {
                "id": str(statistic_id),
                "value": int(statistics_numeric[0]),
                "scope": "complaints",
                "relatedLot": lot_id[0]
            }
            result["statistics"].append(statistic)
            statistic_id += 1

    return result if result["statistics"] else None

def merge_buyer_review_requests_count(release_json, buyer_review_requests_count_data):
    """
    Merge the parsed buyer review requests count data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        buyer_review_requests_count_data (dict): The parsed buyer review requests count data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not buyer_review_requests_count_data:
        logger.warning("No Buyer Review Requests Count data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])
    
    for new_statistic in buyer_review_requests_count_data["statistics"]:
        existing_statistic = next((stat for stat in existing_statistics if stat["relatedLot"] == new_statistic["relatedLot"] and stat["scope"] == "complaints"), None)
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(f"Merged Buyer Review Requests Count data for {len(buyer_review_requests_count_data['statistics'])} lot results")