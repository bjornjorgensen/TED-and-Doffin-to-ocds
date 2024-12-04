# converters/bt_711_LotResult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_value_highest(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the tender value highest (BT-711) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed tender value highest data in OCDS format, or None if no data found.
        Format:
        {
            "bids": {
                "statistics": [
                    {
                        "id": "1",
                        "measure": "highestValidBidValue",
                        "value": 456,
                        "currency": "EUR",
                        "relatedLot": "LOT-0001"
                    }
                ]
            }
        }
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
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for i, lot_result in enumerate(lot_results, 1):
        higher_tender_amount = lot_result.xpath(
            "cbc:HigherTenderAmount",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if higher_tender_amount and lot_id:
            statistic = {
                "id": str(i),
                "measure": "highestValidBidValue",
                "value": float(higher_tender_amount[0].text),
                "currency": higher_tender_amount[0].get("currencyID"),
                "relatedLot": lot_id[0],
            }
            result["bids"]["statistics"].append(statistic)

    return result if result["bids"]["statistics"] else None


def merge_tender_value_highest(
    release_json: dict[str, Any],
    tender_value_highest_data: dict[str, Any] | None,
) -> None:
    """Merge tender value highest data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        tender_value_highest_data: The tender value highest data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not tender_value_highest_data:
        logger.warning("BT-711: No highest tender value data to merge")
        return

    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    for new_stat in tender_value_highest_data["bids"]["statistics"]:
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
        "BT-711: Merged highest tender value data for %d statistics",
        len(tender_value_highest_data["bids"]["statistics"]),
    )
