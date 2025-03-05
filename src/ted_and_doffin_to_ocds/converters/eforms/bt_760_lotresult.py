# converters/bt_760_LotResult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}

SUBMISSION_TYPE_MAPPING = {
    "part-req": "requests",
    "t-esubm": "electronicBids",
    "t-med": "mediumBids",
    "t-micro": "microBids",
    "t-no-eea": "foreignBidsFromNonEU",
    "t-oth-eea": "foreignBidsFromEU",
    "t-small": "smallBids",
    "t-sme": "smeBids",
    "t-verif-inad": "disqualifiedBids",
    "t-verif-inad-low": "tendersAbnormallyLow",
    "tenders": "bids",
    "t-eea": "eeaBids",
    "t-non-eea": "nonEuBids",
    "t-total": "totalBids",
}


def parse_received_submissions_type(xml_content: str | bytes) -> dict | None:
    """Parse BT-760: Types of received submissions for lots.

    Maps counts of different submission types (SME, micro, foreign, etc).
    All tenders are counted regardless of admissibility.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "bids": {
                    "statistics": [
                        {
                            "id": str,
                            "measure": str,  # from SUBMISSION_TYPE_MAPPING
                            "value": int,    # count of submissions of this type
                            "relatedLot": str
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"bids": {"statistics": []}}

        lot_results = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
            "/efext:EformsExtension/efac:NoticeResult/efac:LotResult",
            namespaces=NAMESPACES,
        )

        for lot_result in lot_results:
            lot_id = lot_result.xpath(
                "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=NAMESPACES
            )

            if not lot_id:
                continue

            lot_id = lot_id[0]

            # Find all ReceivedSubmissionsStatistics elements
            statistics_elements = lot_result.xpath(
                "efac:ReceivedSubmissionsStatistics",
                namespaces=NAMESPACES,
            )

            for stat_element in statistics_elements:
                # Get the type code
                stat_code = stat_element.xpath(
                    "efbc:StatisticsCode[@listName='received-submission-type']/text()",
                    namespaces=NAMESPACES,
                )
                if not stat_code:
                    continue

                stat_code = stat_code[0]

                # Get the corresponding count value
                stat_value = stat_element.xpath(
                    "efbc:StatisticsNumeric/text()",
                    namespaces=NAMESPACES,
                )

                # If no value is provided, skip this statistic
                if not stat_value:
                    logger.warning(
                        "Missing value for submission type %s in lot %s",
                        stat_code,
                        lot_id,
                    )
                    continue

                try:
                    value = int(stat_value[0])
                except (ValueError, TypeError):
                    logger.warning(
                        "Invalid value for submission type %s in lot %s: %s",
                        stat_code,
                        lot_id,
                        stat_value[0],
                    )
                    continue

                measure = SUBMISSION_TYPE_MAPPING.get(stat_code)
                if measure:
                    logger.info(
                        "Found submission type %s with value %d for lot %s",
                        measure,
                        value,
                        lot_id,
                    )
                    statistic = {
                        "id": f"{measure}-{lot_id}",
                        "measure": measure,
                        "value": value,
                        "relatedLot": lot_id,
                    }
                    result["bids"]["statistics"].append(statistic)
                else:
                    logger.warning("Unknown submission type code: %s", stat_code)

        return result if result["bids"]["statistics"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing submission types")
        return None


def merge_received_submissions_type(
    release_json: dict, submissions_data: dict | None
) -> None:
    """Merge received submissions type data into the release JSON.

    Updates or adds submission type statistics to bids.statistics array.

    Args:
        release_json: Main OCDS release JSON to update
        submissions_data: Submissions type data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates bids.statistics array if needed
        - Updates existing statistics by measure and relatedLot
        - Maintains unique statistic IDs

    """
    if not submissions_data:
        logger.warning("BT-760: No Received Submissions Type data to merge")
        return

    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    for new_stat in submissions_data["bids"]["statistics"]:
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

    # Renumber the statistics
    for i, stat in enumerate(statistics, start=1):
        stat["id"] = str(i)

    logger.info(
        "BT-760: Merged Received Submissions Type data for %d statistics",
        len(submissions_data["bids"]["statistics"]),
    )
