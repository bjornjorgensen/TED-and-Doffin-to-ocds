# converters/bt_44_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_prize_rank(xml_content: str | bytes) -> dict | None:
    """Parse prize rank information from XML content.

    Extracts information about prizes and their ranks in design contests.
    Creates OCDS-formatted data with prizes ordered by their rank.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        dict: OCDS-formatted dictionary containing prize rank data, or
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
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:Prize", namespaces=namespaces
        )

        if prizes:
            lot_data = {"id": lot_id, "designContest": {"prizes": {"details": []}}}
            prize_list = []

            for prize in prizes:
                rank_code = prize.xpath("cbc:RankCode/text()", namespaces=namespaces)
                prize_data = {"id": ""}  # ID will be set after sorting
                if rank_code:
                    prize_data["rank"] = int(rank_code[0])
                prize_list.append(prize_data)

            # Sort prizes by rank if available, otherwise keep original order
            prize_list.sort(key=lambda x: x.get("rank", float("inf")))

            # Set IDs based on final order
            for i, prize in enumerate(prize_list):
                prize["id"] = str(i)
                if "rank" in prize:
                    del prize[
                        "rank"
                    ]  # Remove rank as it's encoded in the array position

            lot_data["designContest"]["prizes"]["details"] = prize_list
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_prize_rank(
    release_json: dict,
    prize_rank_data: dict | None,
) -> None:
    """Merge prize rank data into the main release.

    Updates the release JSON with prize rank information,
    either by updating existing lots or adding new ones.

    Args:
        release_json: The main release JSON to update
        prize_rank_data: Prize rank data to merge, as returned by parse_prize_rank()

    """
    if not prize_rank_data:
        logger.warning("No Prize Rank data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in prize_rank_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("designContest", {}).setdefault("prizes", {})[
                "details"
            ] = new_lot["designContest"]["prizes"]["details"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Prize Rank data for %d lots",
        len(prize_rank_data["tender"]["lots"]),
    )
