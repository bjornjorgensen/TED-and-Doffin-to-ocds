# converters/bt_712b_lotresult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_buyer_review_complainants_number(xml_content):
    """
    Parse the XML content to extract the buyer review complainants number for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed buyer review complainants number data.
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
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    # Check if the relevant XPath exists
    relevant_xpath = "//efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No buyer review complainants number data found. Skipping parse_buyer_review_complainants_number."
        )
        return None

    result = {"statistics": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces
    )
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)
        if not lot_id:
            continue

        complainants_number = lot_result.xpath(
            "efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']/efbc:StatisticsNumeric/text()",
            namespaces=namespaces,
        )
        if complainants_number:
            statistic = {
                "id": str(len(result["statistics"]) + 1),
                "value": int(complainants_number[0]),
                "measure": "complainants",
                "scope": "complaints",
                "relatedLot": lot_id[0],
            }
            result["statistics"].append(statistic)

    return result if result["statistics"] else None


def merge_buyer_review_complainants_number(release_json, complainants_number_data):
    """
    Merge the parsed buyer review complainants number data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        complainants_number_data (dict): The parsed buyer review complainants number data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not complainants_number_data:
        logger.info("No buyer review complainants number data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])

    for new_statistic in complainants_number_data["statistics"]:
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
        "Merged buyer review complainants number data for %d lots",
        len(complainants_number_data["statistics"]),
    )
