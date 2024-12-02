# converters/bt_42_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_jury_decision_binding(xml_content: str | bytes) -> dict | None:
    """Parse lot jury decision binding information from XML content.

    Extracts information about lots where the jury's decision is binding on the buyer.
    Creates OCDS-formatted data with bindingJuryDecision flag set to True for these lots.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        dict: OCDS-formatted dictionary containing lot jury decision binding data, or
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
        binding_on_buyer_indicator = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cbc:BindingOnBuyerIndicator/text()",
            namespaces=namespaces,
        )

        if (
            binding_on_buyer_indicator
            and binding_on_buyer_indicator[0].lower() == "true"
        ):
            lot_data = {"id": lot_id, "designContest": {"bindingJuryDecision": True}}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_jury_decision_binding(
    release_json: dict,
    lot_jury_decision_binding_data: dict | None,
) -> None:
    """Merge lot jury decision binding data into the main release.

    Updates the release JSON with lot jury decision binding information,
    either by updating existing lots or adding new ones.

    Args:
        release_json: The main release JSON to update
        lot_jury_decision_binding_data: Jury decision binding data to merge, as returned by
            parse_lot_jury_decision_binding()
    """
    if not lot_jury_decision_binding_data:
        logger.warning("No lot jury decision binding data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_jury_decision_binding_data["tender"]["lots"]:
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
        "Merged lot jury decision binding data for %d lots",
        len(lot_jury_decision_binding_data["tender"]["lots"]),
    )
