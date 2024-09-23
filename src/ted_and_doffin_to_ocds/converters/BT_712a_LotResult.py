# converters/BT_712a_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_complainants(xml_content):
    """
    Parse the XML content to extract the Buyer Review Complainants data for each lot result.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "statistics": [
                      {
                          "id": "unique_id",
                          "measure": "complainants",
                          "relatedLot": "lot_id"
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"statistics": []}
    statistic_id = 1

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )
        complainants = lot_result.xpath(
            "efac:AppealRequestsStatistics[efbc:StatisticsCode[@listName='review-type']/text()='complainants']",
            namespaces=namespaces,
        )

        if lot_id and complainants:
            statistic = {
                "id": str(statistic_id),
                "measure": "complainants",
                "relatedLot": lot_id[0],
            }
            result["statistics"].append(statistic)
            statistic_id += 1

    return result if result["statistics"] else None


def merge_buyer_review_complainants(release_json, buyer_review_complainants_data):
    """
    Merge the parsed Buyer Review Complainants data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        buyer_review_complainants_data (dict): The parsed Buyer Review Complainants data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not buyer_review_complainants_data:
        logger.warning("No Buyer Review Complainants data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])

    for new_statistic in buyer_review_complainants_data["statistics"]:
        existing_statistic = next(
            (
                stat
                for stat in existing_statistics
                if stat.get("measure") == "complainants"
                and stat.get("relatedLot") == new_statistic["relatedLot"]
            ),
            None,
        )

        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(
        f"Merged Buyer Review Complainants data for {len(buyer_review_complainants_data['statistics'])} statistics",
    )
