# converters/bt_710_LotResult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_value_lowest(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the lowest tender value for each lot (BT-710).

    BT-710: Value of the admissible tender with the lowest value. Only tenders that are
    admissible and verified may be taken into account.
    Maps to OCDS bids.statistics array with measure "lowestValidBidValue".

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing:
            - bids.statistics (list): List of statistics objects with structure:
                {
                    "id": str,           # Unique identifier for the statistic
                    "measure": str,      # Always "lowestValidBidValue"
                    "value": float,      # Amount of lowest valid bid
                    "currency": str,     # Currency code from currencyID
                    "relatedLots": list  # List containing the lot ID
                }
            Returns None if no relevant data is found.

    Example:
        >>> xml = '''
        <NoticeResult>
          <LotResult>
            <cbc:LowerTenderAmount currencyID="EUR">1230000</cbc:LowerTenderAmount>
            <efac:TenderLot>
              <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            </efac:TenderLot>
          </LotResult>
        </NoticeResult>
        '''
        >>> result = parse_tender_value_lowest(xml)
        >>> print(result)
        {'bids': {'statistics': [{'id': 'lowest-LOT-0001', 'measure': 'lowestValidBidValue',
                                'value': {'amount': 1230000.0, 'currency': 'EUR'},
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
        lower_tender_amount = lot_result.xpath(
            "cbc:LowerTenderAmount",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if lower_tender_amount and lot_id:
            statistic = {
                "id": f"lowest-{lot_id[0]}",
                "measure": "lowestValidBidValue",
                "value": {
                    "amount": float(lower_tender_amount[0].text),
                    "currency": lower_tender_amount[0].get("currencyID"),
                },
                "relatedLots": [lot_id[0]],
            }
            result["bids"]["statistics"].append(statistic)

    return result if result["bids"]["statistics"] else None


def merge_tender_value_lowest(
    release_json: dict, tender_value_lowest_data: dict | None
) -> None:
    """
    Merge the parsed tender value lowest data into the main OCDS release JSON.

    Updates the bids.statistics array in the release JSON with lowest tender values.
    If statistics for the same measure and lot already exist, they are updated;
    otherwise, new statistics are appended.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        tender_value_lowest_data (Optional[Dict]): The parsed tender value lowest
            data to be merged, containing a 'bids.statistics' array.

    Returns:
        None: The function updates the release_json in-place.

    Example:
        >>> release = {'bids': {'statistics': []}}
        >>> data = {'bids': {'statistics': [{'id': '1', 'measure': 'lowestValidBidValue'}]}}
        >>> merge_tender_value_lowest(release, data)
        >>> print(release)
        {'bids': {'statistics': [{'id': '1', 'measure': 'lowestValidBidValue'}]}}
    """
    if not tender_value_lowest_data:
        logger.warning("BT-710: No Tender Value Lowest data to merge")
        return

    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    for new_stat in tender_value_lowest_data["bids"]["statistics"]:
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
        "Merged Tender Value Lowest data for %d statistics",
        len(tender_value_lowest_data["bids"]["statistics"]),
    )
