# converters/opt_321_tender.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_technical_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse tender technical identifiers from lot tenders.

    For each lot tender:
    - Gets tender ID
    - Creates basic bid entries
    - Skips bids that already exist

    Args:
        xml_content: XML content containing tender data

    Returns:
        Optional[Dict]: Dictionary containing bids with IDs, or None if no data.
        Example structure:
        {
            "bids": {
                "details": [
                    {
                        "id": "tender_id"
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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"bids": {"details": []}}

    # Parse LotTender information
    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender", namespaces=namespaces
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )

        if tender_id:
            bid = {"id": tender_id[0]}
            result["bids"]["details"].append(bid)

    return result if result["bids"]["details"] else None


def merge_tender_technical_identifier(
    release_json: dict[str, Any],
    tender_technical_identifier_data: dict[str, Any] | None,
) -> None:
    """Merge tender technical identifier data into the release JSON.

    Args:
        release_json: Target release JSON to update
        tender_technical_identifier_data: Tender data containing bid identifiers

    Effects:
        Updates the bids.details section of release_json with new bids,
        skipping any that already exist

    """
    if not tender_technical_identifier_data:
        logger.info("No Tender Technical Identifier data to merge.")
        return

    bids = release_json.setdefault("bids", {}).setdefault("details", [])

    for new_bid in tender_technical_identifier_data["bids"]["details"]:
        if not any(bid["id"] == new_bid["id"] for bid in bids):
            bids.append(new_bid)

    logger.info(
        "Merged Tender Technical Identifier data for %d bids.",
        len(tender_technical_identifier_data["bids"]["details"]),
    )
