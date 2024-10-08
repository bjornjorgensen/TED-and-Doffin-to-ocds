# converters/bt_635_lotresult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_review_requests_count(xml_content):
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

    result = {"statistics": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces
    )
    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces
        )
        statistics = lot_result.xpath(
            "efac:AppealRequestsStatistics/efbc:StatisticsNumeric/text()",
            namespaces=namespaces,
        )

        if lot_id and statistics:
            statistic = {
                "value": float(statistics[0]),
                "scope": "complaints",
                "relatedLot": lot_id[0],
            }
            result["statistics"].append(statistic)

    return result if result["statistics"] else None


def merge_buyer_review_requests_count(release_json, buyer_review_requests_count_data):
    if not buyer_review_requests_count_data:
        logger.info("No buyer review requests count data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])

    # Find the highest existing id
    max_id = 0
    for stat in existing_statistics:
        try:
            stat_id = int(stat["id"])
            max_id = max(stat_id, max_id)
        except ValueError:
            pass

    # Assign new ids starting from max_id + 1
    for new_statistic in buyer_review_requests_count_data["statistics"]:
        existing_statistic = next(
            (
                stat
                for stat in existing_statistics
                if stat["scope"] == "complaints"
                and stat["relatedLot"] == new_statistic["relatedLot"]
            ),
            None,
        )
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            max_id += 1
            new_statistic["id"] = str(max_id)
            existing_statistics.append(new_statistic)

    logger.info(
        "Merged buyer review requests count data for %d statistics",
        len(buyer_review_requests_count_data["statistics"]),
    )
