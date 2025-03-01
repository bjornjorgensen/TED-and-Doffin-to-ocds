# converters/bt_142_LotResult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Tender result code lookup table - from authority table: http://publications.europa.eu/resource/authority/winner-selection-status
STATUS_CODE_MAPPING = {
    "clos-nw": "No winner was chosen and the competition is closed.",
    "open-nw": "The winner was not yet chosen, but the competition is still ongoing.",
    "selec-w": "At least one winner was chosen.",
}


def parse_winner_chosen(xml_content: str | bytes) -> dict | None:
    """Parse the winner chosen status from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot result information

    Returns:
        Optional[Dict]: Dictionary containing award and lot information, or None if no data found
        The structure follows the format:
        {
            "awards": [
                {
                    "id": str,
                    "status": str,
                    "statusDetails": str,
                    "relatedLots": [str]
                }
            ],
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "status": str
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"awards": [], "tender": {"lots": []}}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        result_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        tender_result_code = lot_result.xpath(
            "cbc:TenderResultCode[@listName='winner-selection-status']/text()",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if result_id and tender_result_code and lot_id:
            result_id = result_id[0]
            tender_result_code = tender_result_code[0]
            lot_id = lot_id[0]

            # Follow eForms guidance for status assignment
            if tender_result_code == "open-nw":
                # For "open-nw", set the lot status to 'active'
                result["tender"]["lots"].append({"id": lot_id, "status": "active"})
            else:
                # Create award for all other cases
                status = "active" if tender_result_code == "selec-w" else "unsuccessful"
                award = {
                    "id": result_id,
                    "status": status,
                    "statusDetails": STATUS_CODE_MAPPING.get(
                        tender_result_code, "Unknown"
                    ),
                    "relatedLots": [lot_id],
                }
                result["awards"].append(award)

    return result if (result["awards"] or result["tender"]["lots"]) else None


def merge_winner_chosen(release_json: dict, winner_chosen_data: dict | None) -> None:
    """Merge winner chosen data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        winner_chosen_data (Optional[Dict]): The source data containing awards and lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by updating award statuses
        and lot information.

    """
    if not winner_chosen_data:
        logger.warning("No winner chosen data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])
    for new_award in winner_chosen_data["awards"]:
        existing_award = next(
            (a for a in existing_awards if a["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award.update(new_award)
        else:
            existing_awards.append(new_award)

    # Remove any existing awards that are not in the new data
    release_json["awards"] = [
        award
        for award in existing_awards
        if any(
            new_award["id"] == award["id"] for new_award in winner_chosen_data["awards"]
        )
    ]

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    for new_lot in winner_chosen_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.update(new_lot)
        else:
            existing_lots.append(new_lot)
    logger.info(
        "Merged winner chosen data for %d awards and %d lots",
        len(winner_chosen_data["awards"]),
        len(winner_chosen_data["tender"]["lots"]),
    )
