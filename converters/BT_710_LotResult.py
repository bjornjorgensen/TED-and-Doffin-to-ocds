# converters/BT_710_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_tender_value_lowest(xml_content):
    """
    Parse the XML content to extract the lowest tender value for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        list: A list of dictionaries containing the parsed data in the format:
              [
                  {
                      "value": float,
                      "currency": str,
                      "relatedLot": str
                  }
              ]
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes 
    if isinstance(xml_content, str): 
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = []

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lower_tender_amount = lot_result.xpath("cbc:LowerTenderAmount", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if lower_tender_amount and lot_id:
            value = float(lower_tender_amount[0].text)
            currency = lower_tender_amount[0].get('currencyID')
            
            result.append({
                "value": value,
                "currency": currency,
                "relatedLot": lot_id[0]
            })

    return result if result else None

def merge_tender_value_lowest(release_json, tender_value_lowest_data):
    """
    Merge the parsed lowest tender value data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        tender_value_lowest_data (list): The parsed lowest tender value data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not tender_value_lowest_data:
        logger.warning("No Tender Value Lowest data to merge")
        return

    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    for index, data in enumerate(tender_value_lowest_data, start=1):
        statistic = {
            "id": str(len(statistics) + index),
            "measure": "lowestValidBidValue",
            "value": data["value"],
            "currency": data["currency"],
            "relatedLot": data["relatedLot"]
        }
        statistics.append(statistic)

    logger.info(f"Merged Tender Value Lowest data for {len(tender_value_lowest_data)} lots")