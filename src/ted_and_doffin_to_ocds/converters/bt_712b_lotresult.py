# converters/bt_712b_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_complainants_bt_712b(xml_content):
    """
    Parse the XML content to extract the number of buyer review complainants for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "statistics": [
                      {
                          "id": "1",
                          "value": 2,
                          "measure": "complainants",
                          "scope": "complaints",
                          "relatedLot": "LOT-0001"
                      }
                  ]
              }
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"statistics": []}
    stat_id = 1

    lot_results = root.xpath(
        "//efac:noticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )
        complainants = lot_result.xpath(
            "efac:AppealRequestsStatistics/efbc:StatisticsNumeric/text()",
            namespaces=namespaces,
        )

        if lot_id and complainants:
            statistic = {
                "id": str(stat_id),
                "value": int(complainants[0]),
                "measure": "complainants",
                "scope": "complaints",
                "relatedLot": lot_id[0],
            }
            result["statistics"].append(statistic)
            stat_id += 1

    return result if result["statistics"] else None


def merge_buyer_review_complainants_bt_712b(
    release_json,
    buyer_review_complainants_data,
):
    """
    Merge the parsed buyer review complainants data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        buyer_review_complainants_data (dict): The parsed buyer review complainants data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not buyer_review_complainants_data:
        logger.warning("No buyer review complainants data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])

    for new_statistic in buyer_review_complainants_data["statistics"]:
        existing_statistic = next(
            (stat for stat in existing_statistics if stat["id"] == new_statistic["id"]),
            None,
        )
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(
        "Merged buyer review complainants data for %d lots",
        len(buyer_review_complainants_data["statistics"]),
    )