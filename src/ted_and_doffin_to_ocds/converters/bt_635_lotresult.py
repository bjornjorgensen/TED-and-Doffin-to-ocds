# converters/bt_635_lotresult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_requests_count(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the buyer review requests count (BT-635) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed buyer review requests count in OCDS format, or None if no data found.
        Format:
        {
            "statistics": [
                {
                    "id": "1",
                    "value": 2,
                    "scope": "complaints",
                    "relatedLot": "LOT-0001"
                }
            ]
        }

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
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )
    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID/text()",
            namespaces=namespaces,
        )
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
    release_json: dict[str, Any],
    buyer_review_requests_data: dict[str, Any] | None,
) -> None:
    """Merge buyer review requests count data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        buyer_review_requests_data: The buyer review requests count data to merge from

    Returns:
        None - modifies release_json in place

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
