import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Mapping for decision reason codes
REASON_CODE_MAPPING = {
    "all-rej": "All tenders, requests to participate or projects were withdrawn or found inadmissible",
    "chan-need": "Decision of the buyer, because of a change in needs",
    "ins-fund": "Decision of the buyer, because of insufficient funds",
    "no-rece": "No tenders, requests to participate or projects were received",
    "no-signed": "The highest ranked tenderer(s) refused to sign the contract",
    "none-rej": "No tenders or requests to participate were received or all were rejected",
    "one-admis": "Only one admissible tender, request to participate or project was received",
    "other": "Other",
    "rev-body": "Decision of a review body or another judicial body",
    "rev-buyer": "Decision of the buyer following a tenderer's request to review the award",
    "tch-pr-error": "Decision of the buyer, not following a tenderer's request to review the award, because of technical or procedural errors",
}


def parse_not_awarded_reason(xml_content: str | bytes) -> dict | None:
    """
    Parse the not awarded reason from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot result information

    Returns:
        Optional[Dict]: Dictionary containing award information, or None if no data found
        The structure follows the format:
        {
            "awards": [
                {
                    "id": str,
                    "status": "unsuccessful",
                    "statusDetails": str,
                    "relatedLots": [str]
                }
            ]
        }
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

    result = {"awards": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        result_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        reason_code = lot_result.xpath(
            "efac:DecisionReason/efbc:DecisionReasonCode[@listName='non-award-justification']/text()",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if result_id and reason_code and lot_id:
            award = {
                "id": result_id[0],
                "status": "unsuccessful",
                "statusDetails": REASON_CODE_MAPPING.get(reason_code[0], "Unknown"),
                "relatedLots": [lot_id[0]],
            }
            result["awards"].append(award)

    return result if result["awards"] else None


def merge_not_awarded_reason(
    release_json: dict, not_awarded_reason_data: dict | None
) -> None:
    """
    Merge not awarded reason data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        not_awarded_reason_data (Optional[Dict]): The source data containing awards
            to be merged. If None, function returns without making changes.
    """
    if not not_awarded_reason_data:
        return

    existing_awards = release_json.setdefault("awards", [])
    for new_award in not_awarded_reason_data["awards"]:
        existing_award = next(
            (a for a in existing_awards if a["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award.update(new_award)
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged not awarded reason data for %d awards",
        len(not_awarded_reason_data["awards"]),
    )
