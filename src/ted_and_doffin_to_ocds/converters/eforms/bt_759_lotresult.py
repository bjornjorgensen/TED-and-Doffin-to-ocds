import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_received_submissions_count(
    xml_content: str | bytes, next_id: int = 1
) -> dict | None:
    """Parse BT-759: Number of received submissions for lots.

    Counts tenders or participation requests, with variants or multiple tenders
    from same tenderer counted as one.

    Args:
        xml_content: XML content to parse, either as string or bytes
        next_id: Next available numeric ID to use for statistics

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "bids": {
                    "statistics": [
                        {
                            "id": str,
                            "value": int,
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

        # Update xpath to use proper namespaces
        lot_results = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
            "/efext:EformsExtension/efac:NoticeResult/efac:LotResult",
            namespaces=NAMESPACES,
        )

        for lot_result in lot_results:
            lot_id = lot_result.xpath(
                "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=NAMESPACES
            )
            count = lot_result.xpath(
                "efac:ReceivedSubmissionsStatistics/efbc:StatisticsNumeric/text()",
                namespaces=NAMESPACES,
            )

            if lot_id and count:
                try:
                    submissions = int(count[0])
                    result["bids"]["statistics"].append(
                        {
                            "id": str(next_id),  # Use sequential numeric id
                            "value": submissions,
                            "measure": "bids",
                            "relatedLot": lot_id[0],
                        }
                    )
                    next_id += 1
                    logger.info(
                        "Found %d submissions for lot %s", submissions, lot_id[0]
                    )
                except ValueError:
                    logger.warning("Invalid submission count: %s", count[0])

        return result if result["bids"]["statistics"] else None

    except Exception:
        logger.exception("Error processing submission counts")
        return None


def merge_received_submissions_count(
    release_json: dict, submissions_data: dict | None
) -> None:
    """Merge received submissions count data into the release JSON.

    Updates or adds submission statistics to bids.statistics array.

    Args:
        release_json: Main OCDS release JSON to update
        submissions_data: Submissions count data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates bids.statistics array if needed
        - Updates existing statistics by measure and relatedLot

    """
    if not submissions_data:
        logger.warning("No submission count data to merge")
        return

    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    # Get next available ID
    next_id = 1
    if statistics:
        existing_ids = [int(stat["id"]) for stat in statistics if stat["id"].isdigit()]
        if existing_ids:
            next_id = max(existing_ids) + 1

    # Update statistics list
    for new_stat in submissions_data["bids"]["statistics"]:
        new_stat["id"] = str(next_id)
        next_id += 1
        statistics.append(new_stat)

    logger.info(
        "Merged submission count data for %d lots",
        len(submissions_data["bids"]["statistics"]),
    )
