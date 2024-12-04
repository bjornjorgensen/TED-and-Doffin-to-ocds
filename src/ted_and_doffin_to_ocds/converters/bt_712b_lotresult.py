import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_complainants_number(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the buyer review complainants number (BT-712(b)) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed buyer review complainants number data in OCDS format, or None if no data found.
        Format:
        {
            "statistics": [
                {
                    "id": "1",
                    "value": 2,
                    "measure": "complainants",
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

    # Check if the relevant XPath exists
    relevant_xpath = "//efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "BT-712(b): No buyer review complainants number data found in the document."
        )
        return None

    result = {"statistics": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for i, lot_result in enumerate(lot_results, 1):
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID/text()",
            namespaces=namespaces,
        )
        if not lot_id:
            continue

        complainants_number = lot_result.xpath(
            "efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']/efbc:StatisticsNumeric/text()",
            namespaces=namespaces,
        )
        if complainants_number:
            statistic = {
                "id": str(i),
                "value": int(complainants_number[0]),
                "measure": "complainants",
                "scope": "complaints",
                "relatedLot": lot_id[0],
            }
            result["statistics"].append(statistic)

    return result if result["statistics"] else None


def merge_buyer_review_complainants_number(
    release_json: dict[str, Any],
    complainants_number_data: dict[str, Any] | None,
) -> None:
    """Merge buyer review complainants number data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        complainants_number_data: The buyer review complainants number data to merge from

    Returns:
        None - modifies release_json in place
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
