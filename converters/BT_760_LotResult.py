# converters/BT_760_LotResult.py

import logging
from lxml import etree

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
    "tenders": "bids",
    "t-eea": "eeaBids",
    "t-non-eea": "nonEuBids",
    "t-total": "totalBids",
}


def parse_received_submissions_type(xml_content):
    """
    Parse the XML content to extract the Received Submissions Type information.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data if found, None otherwise.
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

    result = {"bids": {"statistics": []}}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces
    )

    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces
        )
        statistics = lot_result.xpath(
            "efac:ReceivedSubmissionsStatistics/efbc:StatisticsCode[@listName='received-submission-type']/text()",
            namespaces=namespaces,
        )

        for stat in statistics:
            measure = map_statistic_code(stat)
            if measure:
                statistic = {
                    "id": f"{measure}-{lot_id[0]}" if lot_id else f"{measure}-unknown",
                    "measure": measure,
                    "relatedLots": [lot_id[0]] if lot_id else None,
                }
                result["bids"]["statistics"].append(statistic)

    return result if result["bids"]["statistics"] else None


def map_statistic_code(code):
    """Map the statistic code to the corresponding OCDS measure."""
    return SUBMISSION_TYPE_MAPPING.get(code)


def merge_received_submissions_type(release_json, received_submissions_data):
    """
    Merge the parsed Received Submissions Type data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        received_submissions_data (dict): The parsed Received Submissions Type data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not received_submissions_data:
        logger.warning("No Received Submissions Type data to merge")
        return

    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    for new_stat in received_submissions_data["bids"]["statistics"]:
        existing_stat = next(
            (
                stat
                for stat in statistics
                if stat["measure"] == new_stat["measure"]
                and stat.get("relatedLots") == new_stat.get("relatedLots")
            ),
            None,
        )
        if existing_stat:
            existing_stat.update(new_stat)
        else:
            statistics.append(new_stat)

    # Renumber the statistics
    for i, stat in enumerate(statistics, start=1):
        stat["id"] = str(i)

    logger.info(
        f"Merged Received Submissions Type data for {len(received_submissions_data['bids']['statistics'])} statistics"
    )
