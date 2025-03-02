import logging
import re
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_identifier_reference(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse tender identifier references from lot results.

    For each lot result:
    - Gets tender IDs from LotTender elements
    - Creates award with relatedBids array containing all tender IDs

    Args:
        xml_content: XML content containing lot result data

    Returns:
        Optional[Dict]: Dictionary containing awards with related bids, or None if no data.
        Example structure:
        {
            "awards": [
                {
                    "relatedBids": ["TEN-0001", "TEN-0002", ...]
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
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"awards": []}
    pattern = re.compile(r"^TEN-\d{4}$")

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces
    )

    for lot_result in lot_results:
        lot_tenders = lot_result.xpath(
            "efac:LotTender/cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )

        # Filter out IDs that don't match the required pattern
        valid_lot_tenders = [tid for tid in lot_tenders if pattern.match(tid)]

        if valid_lot_tenders:
            # Get lot ID if available (optional, for better award mapping)
            lot_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)
            award_entry = {"relatedBids": valid_lot_tenders}

            # Add lot ID reference if available
            if lot_id:
                award_entry["lotID"] = lot_id[0]

            result["awards"].append(award_entry)

    return result if result["awards"] else None


def merge_tender_identifier_reference(
    release_json: dict[str, Any], tender_identifier_data: dict[str, Any] | None
) -> None:
    """Merge tender identifier data into the release JSON.

    Args:
        release_json: Target release JSON to update
        tender_identifier_data: Tender data containing related bids

    Effects:
        Updates the awards section of release_json with relatedBids arrays,
        combining bid references for the same award

    """
    if not tender_identifier_data:
        logger.info("No Tender Identifier Reference data to merge.")
        return

    awards = release_json.setdefault("awards", [])

    # Ensure we have at least one award to add bids to
    if not awards:
        awards.extend(tender_identifier_data["awards"])
    else:
        # Add all related bids to the last award
        for new_award in tender_identifier_data["awards"]:
            if awards[-1].get("relatedBids"):
                awards[-1]["relatedBids"].extend(new_award["relatedBids"])
            else:
                awards[-1]["relatedBids"] = new_award["relatedBids"]

    # Remove any duplicates from relatedBids and ensure consistent order
    if awards and "relatedBids" in awards[-1]:
        awards[-1]["relatedBids"] = sorted(set(awards[-1]["relatedBids"]))

    logger.info(
        "Merged Tender Identifier Reference data for %d awards.",
        len(tender_identifier_data["awards"]),
    )
