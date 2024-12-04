import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_ranked(xml_content: str | bytes) -> dict | None:
    """Parse tender ranked information from XML content following BT-1711.

    Extracts tender ranking indicator information and maps it to bid details.
    For each LotTender, creates a bid with hasRank and relatedLots properties.

    Args:
        xml_content: XML string or bytes containing the notice result data

    Returns:
        Optional[Dict]: Dictionary containing bids with ranking info, or None if no bids found
        Format: {"bids": {"details": [{"id": str, "hasRank": bool, "relatedLots": list[str]}]}}
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

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath(
        "//efext:EformsExtension/efac:NoticeResult/efac:LotTender[efbc:TenderRankedIndicator and cbc:ID[@schemeName='tender']]",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        try:
            tender_id = lot_tender.xpath(
                "cbc:ID[@schemeName='tender']/text()",
                namespaces=namespaces,
            )[0]
            ranked_indicator = lot_tender.xpath(
                "efbc:TenderRankedIndicator/text()",
                namespaces=namespaces,
            )[0]
            lot_id = lot_tender.xpath(
                "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                namespaces=namespaces,
            )[0]

            bid = {
                "id": tender_id,
                "hasRank": ranked_indicator.lower() == "true",
                "relatedLots": [lot_id],
            }
            result["bids"]["details"].append(bid)
        except (IndexError, AttributeError) as e:
            logger.warning("Skipping incomplete lot tender: %s", e)
            continue

    return result if result["bids"]["details"] else None


def merge_tender_ranked(release_json: dict, tender_ranked_data: dict | None) -> None:
    """Merge tender ranked data into the release JSON.

    Updates or adds bid ranking information in the release JSON document.
    Handles merging of bid details including hasRank property.

    Args:
        release_json: The target release JSON document to update
        tender_ranked_data: The tender ranked data to merge

    Returns:
        None: Modifies release_json in place
    """
    if not tender_ranked_data:
        logger.warning("No Tender Ranked data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])

    for new_bid in tender_ranked_data["bids"]["details"]:
        existing_bid = next(
            (bid for bid in existing_bids if bid["id"] == new_bid["id"]),
            None,
        )
        if existing_bid:
            existing_bid.update(new_bid)
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged Tender Ranked data for %d bids",
        len(tender_ranked_data["bids"]["details"]),
    )
