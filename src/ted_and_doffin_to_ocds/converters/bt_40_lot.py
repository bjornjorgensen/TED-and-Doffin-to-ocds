# converters/bt_40_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_selection_criteria_second_stage(xml_content: str | bytes) -> dict | None:
    """Parse lot selection criteria for second stage from XML content.

    Extracts information about lots where selection criteria will be used for second stage
    invitations. Creates OCDS-formatted data with forReduction flag set to True for
    these lots.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        dict: OCDS-formatted dictionary containing lot selection criteria data, or
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
        selection_criteria = lot.xpath(
            ".//cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:SelectionCriteria[efbc:SecondStageIndicator='true']",
            namespaces=namespaces,
        )

        if selection_criteria:
            lot_data = {
                "id": lot_id,
                "selectionCriteria": {"criteria": [{"forReduction": True}]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_selection_criteria_second_stage(
    release_json: dict,
    lot_selection_criteria_data: dict | None,
) -> None:
    """Merge lot selection criteria second stage data into the main release.

    Updates the release JSON with lot selection criteria information for second stage,
    either by updating existing lots or adding new ones.

    Args:
        release_json: The main release JSON to update
        lot_selection_criteria_data: Selection criteria data to merge, as returned by
            parse_lot_selection_criteria_second_stage()

    """
    if not lot_selection_criteria_data:
        logger.warning("No lot selection criteria second stage data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_selection_criteria_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_criteria = existing_lot.setdefault(
                "selectionCriteria",
                {},
            ).setdefault("criteria", [])
            for new_criterion in new_lot["selectionCriteria"]["criteria"]:
                existing_criterion = next(
                    (c for c in existing_criteria if "forReduction" in c),
                    None,
                )
                if existing_criterion:
                    existing_criterion.update(new_criterion)
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged lot selection criteria second stage data for %d lots",
        len(lot_selection_criteria_data["tender"]["lots"]),
    )
