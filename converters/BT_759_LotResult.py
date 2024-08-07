# converters/BT_759_LotResult.py

import logging
from lxml import etree
from constants import global_statistic_id

logger = logging.getLogger(__name__)

def parse_received_submissions_count(xml_content):
    """
    Parse the XML content to extract the received submissions count for each lot result.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "bids": {
                      "statistics": [
                          {
                              "id": "unique_id",
                              "value": int_value,
                              "relatedLots": ["lot_id"]
                          }
                      ]
                  }
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

    result = {"bids": {"statistics": []}}

    global global_statistic_id  # Use the global counter

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        submissions_count = lot_result.xpath("efac:ReceivedSubmissionsStatistics/efbc:StatisticsNumeric/text()", namespaces=namespaces)

        if lot_id and submissions_count:
            result["bids"]["statistics"].append({
                "id": str(global_statistic_id),  # Assign the global ID
                "value": int(submissions_count[0]),
                "measure": "bids", 
                "relatedLots": [lot_id[0]]
            })
            global_statistic_id += 1  # Increment the global counter

    return result if result["bids"]["statistics"] else None

def merge_received_submissions_count(release_json, received_submissions_data):
    """
    Merge the parsed received submissions count data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        received_submissions_data (dict): The parsed received submissions count data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not received_submissions_data:
        logger.warning("No received submissions count data to merge")
        return

    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    for new_stat in received_submissions_data["bids"]["statistics"]:
        existing_stat = next(
            (stat for stat in statistics if stat["measure"] == new_stat["measure"] and stat.get("relatedLots") == new_stat.get("relatedLots")), 
            None
        )
        if existing_stat:
            # Update based on the measure
            if new_stat["measure"] == "bids":
                existing_stat["value"] = new_stat["value"] 
            else:
                existing_stat["value"] = new_stat["value"]  
        else:
            statistics.append(new_stat)  # Append if no match found

    logger.info(f"Merged received submissions count data for {len(received_submissions_data['bids']['statistics'])} lots")