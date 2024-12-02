# converters/bt_45_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_rewards_other(xml_content: str | bytes) -> dict | None:
    """Parse lot rewards and prize descriptions from XML content.

    Extracts information about prizes and their descriptions for each lot.
    Creates OCDS-formatted data with prize descriptions and IDs.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        dict: OCDS-formatted dictionary containing prize description data, or
        None if no relevant data is found
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        prizes = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:Prize",
            namespaces=namespaces,
        )

        lot_data = {"id": lot_id, "designContest": {"prizes": {"details": []}}}

        for idx, prize in enumerate(prizes):
            description = prize.xpath("cbc:Description/text()", namespaces=namespaces)
            if description:
                prize_data = {"id": str(idx), "description": description[0]}
                lot_data["designContest"]["prizes"]["details"].append(prize_data)

        if lot_data["designContest"]["prizes"]["details"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_rewards_other(
    release_json: dict,
    lot_rewards_other_data: dict | None,
) -> None:
    """Merge lot rewards and prize description data into the main release.

    Updates the release JSON with prize descriptions, either by updating existing
    prize details or adding new ones while preserving existing data like prize ranks.

    Args:
        release_json: The main release JSON to update
        lot_rewards_other_data: Prize description data to merge, as returned by
            parse_lot_rewards_other()
    """
    if not lot_rewards_other_data:
        logger.warning("No Lot Rewards Other data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_rewards_other_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_prizes = (
                existing_lot.setdefault("designContest", {})
                .setdefault("prizes", {})
                .setdefault("details", [])
            )
            for new_prize in new_lot["designContest"]["prizes"]["details"]:
                existing_prize = next(
                    (
                        prize
                        for prize in existing_prizes
                        if prize["id"] == new_prize["id"]
                    ),
                    None,
                )
                if existing_prize:
                    existing_prize.update(new_prize)
                else:
                    existing_prizes.append(new_prize)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Lot Rewards Other data for %d lots",
        len(lot_rewards_other_data["tender"]["lots"]),
    )
