# converters/bt_712b_lotresult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_complainants_number(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the buyer review complainants number for each lot (BT-712(b)).

    BT-712(b): Part of BT-712 which specifies the number of organisations that requested
    the buyer to review decisions. Maps to OCDS statistics array with measure "complainants"
    and scope "complaints".

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing:
            - statistics (list): List of statistics objects with structure:
                {
                    "id": str,           # Unique identifier for the statistic
                    "value": int,        # Number of complainant organizations
                    "measure": str,      # Always "complainants"
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
        >>> result = parse_buyer_review_complainants_number(xml)
        >>> print(result)
        {'statistics': [{'id': '1', 'value': 2, 'measure': 'complainants',
                        'scope': 'complaints', 'relatedLot': 'LOT-0001'}]}
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
            "BT-712(b): No buyer review complainants number data found in the document."
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


def merge_buyer_review_complainants_number(
    release_json: dict, complainants_number_data: dict | None
) -> None:
    """
    Merge the parsed buyer review complainants number data into the main OCDS release JSON.

    Updates the statistics array in the release JSON with complaint statistics.
    If statistics for the same measure and lot already exist, they are updated;
    otherwise, new statistics are appended.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        complainants_number_data (Optional[Dict]): The parsed buyer review complainants
            number data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    Example:
        >>> release = {'statistics': []}
        >>> data = {'statistics': [{'id': '1', 'value': 2, 'measure': 'complainants'}]}
        >>> merge_buyer_review_complainants_number(release, data)
        >>> print(release)
        {'statistics': [{'id': '1', 'value': 2, 'measure': 'complainants'}]}
    """
    if not complainants_number_data:
        logger.info("BT-712(b): No buyer review complainants number data to merge")
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
        "BT-712(b): Merged buyer review complainants number data for %d lots",
        len(complainants_number_data["statistics"]),
    )
