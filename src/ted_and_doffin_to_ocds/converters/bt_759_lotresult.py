# converters/bt_759_LotResult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_received_submissions_count(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the received submissions count for each lot (BT-759).

    BT-759: Number of tenders or requests to participate received. Tenders including
    variants or multiple tenders submitted (for one lot) by the same tenderer should
    be counted as one tender.
    Maps to OCDS bids.statistics array.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing:
            - bids.statistics (list): List of statistics objects with structure:
                {
                    "id": str,           # Unique identifier for the statistic
                    "value": int,        # Number of submissions received
                    "measure": str,      # Always "bids"
                    "relatedLots": list  # List containing the lot ID
                }
            Returns None if no relevant data is found.

    Example:
        >>> xml = '''
        <NoticeResult>
          <LotResult>
            <ReceivedSubmissionsStatistics>
              <StatisticsNumeric>12</StatisticsNumeric>
            </ReceivedSubmissionsStatistics>
            <TenderLot>
              <ID>LOT-0001</ID>
            </TenderLot>
          </LotResult>
        </NoticeResult>
        '''
        >>> result = parse_received_submissions_count(xml)
        >>> print(result)
        {'bids': {'statistics': [{'id': 'bids-LOT-0001', 'value': 12,
                                'measure': 'bids', 'relatedLots': ['LOT-0001']}]}}
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
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
        submissions_count = lot_result.xpath(
            "efac:ReceivedSubmissionsStatistics/efbc:StatisticsNumeric/text()",
            namespaces=namespaces,
        )

        if lot_id and submissions_count:
            result["bids"]["statistics"].append(
                {
                    "id": f"bids-{lot_id[0]}",
                    "value": int(submissions_count[0]),
                    "measure": "bids",
                    "relatedLots": [lot_id[0]],
                },
            )

    return result if result["bids"]["statistics"] else None


def merge_received_submissions_count(
    release_json: dict, received_submissions_data: dict | None
) -> None:
    """
    Merge the parsed received submissions count data into the main OCDS release JSON.

    Updates the bids.statistics array in the release JSON with submission counts.
    If statistics for the same measure and lot already exist, they are updated;
    otherwise, new statistics are appended.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        received_submissions_data (Optional[Dict]): The parsed received submissions
            count data to be merged, containing a 'bids.statistics' array.

    Returns:
        None: The function updates the release_json in-place.

    Example:
        >>> release = {'bids': {'statistics': []}}
        >>> data = {'bids': {'statistics': [{'id': '1', 'value': 12, 'measure': 'bids'}]}}
        >>> merge_received_submissions_count(release, data)
        >>> print(release)
        {'bids': {'statistics': [{'id': '1', 'value': 12, 'measure': 'bids'}]}}
    """
    if not received_submissions_data:
        logger.warning("BT-759: No received submissions count data to merge")
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
        "BT-759: Merged received submissions count data for %d lots",
        len(received_submissions_data["bids"]["statistics"]),
    )
