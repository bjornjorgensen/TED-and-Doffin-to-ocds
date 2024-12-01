# converters/bt_760_LotResult.py

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


def parse_received_submissions_type(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the Received Submissions Type information (BT-760).

    BT-760: The type of tenders or requests to participate received. Maps counts for
    different types of submissions (SME, micro, foreign, etc). All tenders are counted,
    regardless of admissibility.
    Maps to OCDS bids.statistics array with specific measures for each type.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing:
            - bids.statistics (list): List of statistics objects with structure:
                {
                    "id": str,           # Unique identifier for the statistic
                    "measure": str,      # Type of submission from mapping table
                    "relatedLots": list  # List containing the lot ID
                }
            Returns None if no relevant data is found.

    Example:
        >>> xml = '''
        <NoticeResult>
          <LotResult>
            <ReceivedSubmissionsStatistics>
              <StatisticsCode listName="received-submission-type">t-sme</StatisticsCode>
            </ReceivedSubmissionsStatistics>
            <TenderLot>
              <ID>LOT-0001</ID>
            </TenderLot>
          </LotResult>
        </NoticeResult>
        '''
        >>> result = parse_received_submissions_type(xml)
        >>> print(result)
        {'bids': {'statistics': [{'id': 'smeBids-LOT-0001', 'measure': 'smeBids',
                                'relatedLots': ['LOT-0001']}]}}
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
        "//efac:NoticeResult/efac:LotResult",  # Fixed capitalization
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
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


def map_statistic_code(code: str) -> str | None:
    """
    Map the statistic code to the corresponding OCDS measure.

    Args:
        code (str): The received submission type code from the XML.

    Returns:
        Optional[str]: The mapped OCDS measure or None if not found.
    """
    return SUBMISSION_TYPE_MAPPING.get(code)


def merge_received_submissions_type(
    release_json: dict, received_submissions_data: dict | None
) -> None:
    """
    Merge the parsed Received Submissions Type data into the main OCDS release JSON.

    Updates the bids.statistics array in the release JSON with submission type statistics.
    If statistics for the same measure and lot already exist, they are updated;
    otherwise, new statistics are appended.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        received_submissions_data (Optional[Dict]): The parsed submissions type data
            to be merged, containing a 'bids.statistics' array.

    Returns:
        None: The function updates the release_json in-place.

    Example:
        >>> release = {'bids': {'statistics': []}}
        >>> data = {'bids': {'statistics': [{'id': '1', 'measure': 'smeBids'}]}}
        >>> merge_received_submissions_type(release, data)
        >>> print(release)
        {'bids': {'statistics': [{'id': '1', 'measure': 'smeBids'}]}}
    """
    if not received_submissions_data:
        logger.warning("BT-760: No Received Submissions Type data to merge")
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
        "BT-760: Merged Received Submissions Type data for %d statistics",
        len(received_submissions_data["bids"]["statistics"]),
    )
