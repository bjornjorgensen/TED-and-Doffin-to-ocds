import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_value_lowest(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the tender value lowest (BT-710) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed tender value lowest data in OCDS format, or None if no data found.
        Format:
        {
            "bids": {
                "statistics": [
                    {
                        "id": "1",
                        "measure": "lowestValidBidValue",
                        "value": 1230000,
                        "currency": "EUR",
                        "relatedLot": "LOT-0001"
                    }
                ]
            }
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("BT-710: Failed to parse XML")
        return None

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

    if not lot_results:
        logger.debug("BT-710: No LotResult elements found in XML")
        return None

    for i, lot_result in enumerate(lot_results, 1):
        lower_tender_amount = lot_result.xpath(
            "cbc:LowerTenderAmount",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if lower_tender_amount and lot_id:
            try:
                value = (
                    float(lower_tender_amount[0].text)
                    if lower_tender_amount[0].text
                    else None
                )
                currency = lower_tender_amount[0].get("currencyID")

                if value is None or currency is None:
                    logger.warning(
                        "BT-710: Missing value or currency for lot %s", lot_id[0]
                    )
                    continue

                statistic = {
                    "id": str(i),
                    "measure": "lowestValidBidValue",
                    "value": value,
                    "currency": currency,
                    "relatedLot": lot_id[0],
                }
                result["bids"]["statistics"].append(statistic)
                logger.debug(
                    "BT-710: Added lowest tender value %s %s for lot %s",
                    value,
                    currency,
                    lot_id[0],
                )
            except (ValueError, TypeError) as e:
                logger.warning(
                    "BT-710: Invalid value format in LowerTenderAmount for lot %s: %s",
                    lot_id[0] if lot_id else "unknown",
                    str(e),
                )
        elif lower_tender_amount:
            logger.warning("BT-710: Found LowerTenderAmount but missing lot ID")
        elif lot_id:
            logger.debug("BT-710: No LowerTenderAmount found for lot %s", lot_id[0])

    if not result["bids"]["statistics"]:
        logger.debug("BT-710: No valid lowest tender values found")
        return None

    logger.info(
        "BT-710: Successfully extracted %d lowest tender values",
        len(result["bids"]["statistics"]),
    )
    return result


def merge_tender_value_lowest(
    release_json: dict[str, Any],
    tender_value_lowest_data: dict[str, Any] | None,
) -> None:
    """Merge tender value lowest data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        tender_value_lowest_data: The tender value lowest data to merge from

    Returns:
        None - modifies release_json in place

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
                and stat.get("relatedLot") == new_stat.get("relatedLot")
            ),
            None,
        )
        if existing_stat:
            existing_stat.update(new_stat)
        else:
            statistics.append(new_stat)

    # Reassign ids to ensure they are sequential
    for i, stat in enumerate(statistics, 1):
        stat["id"] = str(i)

    logger.info(
        "BT-710: Merged Tender Value Lowest data for %d statistics (lowestValidBidValue)",
        len(tender_value_lowest_data["bids"]["statistics"]),
    )
