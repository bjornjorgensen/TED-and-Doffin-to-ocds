# converters/BT_40_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_selection_criteria_second_stage(xml_content):
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        selection_criteria = lot.xpath(
            ".//efac:SelectionCriteria[efbc:SecondStageIndicator='true']",
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
    release_json, lot_selection_criteria_data,
):
    if not lot_selection_criteria_data:
        logger.warning("No lot selection criteria second stage data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_selection_criteria_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_criteria = existing_lot.setdefault(
                "selectionCriteria", {},
            ).setdefault("criteria", [])
            for new_criterion in new_lot["selectionCriteria"]["criteria"]:
                existing_criterion = next(
                    (c for c in existing_criteria if "forReduction" in c), None,
                )
                if existing_criterion:
                    existing_criterion.update(new_criterion)
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged lot selection criteria second stage data for {len(lot_selection_criteria_data['tender']['lots'])} lots",
    )
