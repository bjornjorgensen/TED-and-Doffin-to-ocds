import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_complainants_code(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the buyer review complainants code (BT-712(a)) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed buyer review complainants code data in OCDS format, or None if no data found.
        Format:
        {
            "statistics": [
                {
                    "id": "1",
                    "value": 2,
                    "measure": "complainants",
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

    relevant_xpath = "//efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "BT-712(a): No buyer review complainants code data found in the document."
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

        complainants_code = lot_result.xpath(
            "efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']/efbc:StatisticsCode/text()",
            namespaces=namespaces,
        )

        complainants_value = lot_result.xpath(
            "efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']/efbc:StatisticsNumeric/text()",
            namespaces=namespaces,
        )

        if complainants_code and complainants_code[0] == "complainants":
            statistic = {
                "id": str(i),
                "measure": "complainants",
                "relatedLot": lot_id[0],
            }
            if complainants_value:
                try:
                    statistic["value"] = int(complainants_value[0])
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid numeric value for complainants: %s",
                        complainants_value[0],
                    )

            result["statistics"].append(statistic)

    return result if result["statistics"] else None


def merge_buyer_review_complainants_code(
    release_json: dict[str, Any],
    complainants_code_data: dict[str, Any] | None,
) -> None:
    """Merge buyer review complainants code data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        complainants_code_data: The buyer review complainants code data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not complainants_code_data:
        logger.info("BT-712(a): No buyer review complainants code data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])

    for new_statistic in complainants_code_data["statistics"]:
        existing_index = next(
            (
                i
                for i, stat in enumerate(existing_statistics)
                if stat.get("measure") == "complainants"
                and stat.get("relatedLot") == new_statistic["relatedLot"]
            ),
            None,
        )
        if existing_index is not None:
            # Replace the existing statistic entirely with the new one
            existing_statistics[existing_index] = new_statistic
        else:
            existing_statistics.append(new_statistic)

    logger.info(
        "BT-712(a): Merged buyer review complainants code data for %d lots",
        len(complainants_code_data["statistics"]),
    )
