# converters/bt_635_lotresult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_requests_count(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the buyer review requests count for each lot (BT-635).

    BT-635: The number of requests the buyer received to review any of its decisions.
    Maps to OCDS statistics array with scope "complaints".

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing:
            - statistics (list): List of statistics objects with structure:
                {
                    "id": str,           # Unique identifier for the statistic
                    "value": int,        # Number of buyer review requests
                    "scope": str,        # Always "complaints"
                    "relatedLot": str    # ID of the lot this statistic relates to
                }
            Returns None if no relevant data is found.

    Example:
        >>> xml = '''
        <NoticeResult>
          <LotResult>
            <AppealRequestsStatistics>
              <StatisticsNumeric>2</StatisticsNumeric>
            </AppealRequestsStatistics>
            <TenderLot>
              <ID>LOT-0001</ID>
            </TenderLot>
          </LotResult>
        </NoticeResult>
        '''
        >>> result = parse_buyer_review_requests_count(xml)
        >>> print(result)
        {'statistics': [{'id': '1', 'value': 2, 'scope': 'complaints', 'relatedLot': 'LOT-0001'}]}
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

    # XPath for BT-635: Number of buyer review requests
    relevant_xpath = "//efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "BT-635: No buyer review requests count data found in the document."
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

        appeal_requests = lot_result.xpath(
            "efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efbc:StatisticsNumeric/text()",
            namespaces=namespaces,
        )
        if appeal_requests:
            statistic = {
                "id": str(len(result["statistics"]) + 1),
                "value": int(appeal_requests[0]),
                "scope": "complaints",
                "relatedLot": lot_id[0],
            }
            result["statistics"].append(statistic)

    return result if result["statistics"] else None


def merge_buyer_review_requests_count(
    release_json: dict, buyer_review_requests_data: dict | None
) -> None:
    """
    Merge the parsed buyer review requests count data into the main OCDS release JSON.

    Updates the statistics array in the release JSON with complaint statistics from
    buyer review requests. If statistics for the same ID already exist, they are
    updated; otherwise, new statistics are appended.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated. Must contain
            or accept a 'statistics' array.
        buyer_review_requests_data (Optional[Dict]): The parsed buyer review requests
            count data to be merged, containing a 'statistics' array.

    Returns:
        None: The function updates the release_json in-place.

    Example:
        >>> release = {'statistics': []}
        >>> data = {'statistics': [{'id': '1', 'value': 2, 'scope': 'complaints'}]}
        >>> merge_buyer_review_requests_count(release, data)
        >>> print(release)
        {'statistics': [{'id': '1', 'value': 2, 'scope': 'complaints'}]}
    """
    if not buyer_review_requests_data:
        logger.info("No buyer review requests count data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])

    for new_statistic in buyer_review_requests_data["statistics"]:
        existing_statistic = next(
            (stat for stat in existing_statistics if stat["id"] == new_statistic["id"]),
            None,
        )
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(
        "Merged buyer review requests count data for %d lots",
        len(buyer_review_requests_data["statistics"]),
    )
