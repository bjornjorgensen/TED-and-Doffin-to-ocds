# converters/BT_712_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_result_complaints(xml_content):
    """
    Parse the XML content to extract the buyer review complainants information for each lot result.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        list: A list of dictionaries containing the parsed complaints data.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes 
    if isinstance(xml_content, str): 
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    results = []

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if lot_id:
            statistics_code = lot_result.xpath("efac:AppealRequestsStatistics/efbc:StatisticsCode[@listName='review-type']/text()", namespaces=namespaces)
            statistics_numeric = lot_result.xpath("efac:AppealRequestsStatistics/efbc:StatisticsNumeric/text()", namespaces=namespaces)
            
            if statistics_code and statistics_numeric:
                result = {
                    "relatedLot": lot_id[0],
                    "measure": statistics_code[0],
                    "value": int(statistics_numeric[0])
                }
                results.append(result)

    return results if results else None

def merge_lot_result_complaints(release_json, lot_result_complaints_data):
    """
    Merge the parsed buyer review complainants data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_result_complaints_data (list): The parsed complaints data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_result_complaints_data:
        logger.warning("No Lot Result Complaints data to merge")
        return

    statistics = release_json.setdefault("statistics", [])
    
    for complaint_data in lot_result_complaints_data:
        existing_statistic = next((stat for stat in statistics if stat.get("relatedLot") == complaint_data["relatedLot"]), None)
        
        if existing_statistic:
            # Update existing statistic
            existing_statistic["value"] = complaint_data["value"]
            if "measure" not in existing_statistic:
                existing_statistic["measure"] = complaint_data["measure"]
        else:
            # Create new statistic
            statistic = {
                "id": str(len(statistics) + 1),
                "measure": complaint_data["measure"],
                "value": complaint_data["value"],
                "relatedLot": complaint_data["relatedLot"],
                "scope": "complaints"
            }
            statistics.append(statistic)

    logger.info(f"Merged Lot Result Complaints data for {len(lot_result_complaints_data)} lots")