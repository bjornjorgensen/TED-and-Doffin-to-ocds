# converters/bt_41_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_following_contract(xml_content: str | bytes) -> dict | None:
    """Parse lot following contract information from XML content.

    Extracts information about lots where a service contract following the contest
    will be awarded to one of the winners. Creates OCDS-formatted data with
    followUpContracts flag set to True for these lots.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        dict: OCDS-formatted dictionary containing lot following contract data, or
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
        followup_contract_indicator = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cbc:FollowupContractIndicator/text()",
            namespaces=namespaces,
        )

        if (
            followup_contract_indicator
            and followup_contract_indicator[0].lower() == "true"
        ):
            lot_data = {"id": lot_id, "designContest": {"followUpContracts": True}}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_following_contract(
    release_json: dict,
    lot_following_contract_data: dict | None,
) -> None:
    """Merge lot following contract data into the main release.

    Updates the release JSON with lot following contract information,
    either by updating existing lots or adding new ones.

    Args:
        release_json: The main release JSON to update
        lot_following_contract_data: Following contract data to merge, as returned by
            parse_lot_following_contract()
    """
    if not lot_following_contract_data:
        logger.warning("No lot following contract data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_following_contract_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("designContest", {}).update(
                new_lot["designContest"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged lot following contract data for %d lots",
        len(lot_following_contract_data["tender"]["lots"]),
    )
