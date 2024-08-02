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
        dict: A dictionary containing the parsed data in the format:
              {
                  "bids": {
                      "statistics": [
                          {
                              "id": "statistic_id",
                              "measure": "lowestValidBidValue",
                              "value": float_value,
                              "currency": "currency_code",
                              "relatedLot": "lot_id"
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
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1'
    }

    result = {"bids": {"statistics": []}}
    statistic_id = 1

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lower_tender_amount = lot_result.xpath("cbc:LowerTenderAmount/text()", namespaces=namespaces)
        currency = lot_result.xpath("cbc:LowerTenderAmount/@currencyID", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)

        if lower_tender_amount and currency and lot_id:
            statistic = {
                "id": str(statistic_id),
                "measure": "lowestValidBidValue",
                "value": float(lower_tender_amount[0]),
                "currency": currency[0],
                "relatedLot": lot_id[0]
            }
            result["bids"]["statistics"].append(statistic)
            statistic_id += 1

    return result if result["bids"]["statistics"] else None

def merge_tender_value_lowest(release_json, tender_value_lowest_data):
    """
    Merge the parsed lowest tender value data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        tender_value_lowest_data (dict): The parsed lowest tender value data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not tender_value_lowest_data:
        logger.warning("No Tender Value Lowest data to merge")
        return

    bids = release_json.setdefault("bids", {})
    existing_statistics = bids.setdefault("statistics", [])
    
    for new_statistic in tender_value_lowest_data["bids"]["statistics"]:
        existing_statistic = next((stat for stat in existing_statistics if stat["id"] == new_statistic["id"]), None)
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(f"Merged Tender Value Lowest data for {len(tender_value_lowest_data['bids']['statistics'])} statistics")