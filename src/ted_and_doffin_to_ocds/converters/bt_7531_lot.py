# converters/bt_7531_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

WEIGHT_MAPPING = {
    "per-exa": "percentageExact",
    "per-ran": "percentageRangeMiddle",
    "dec-exa": "decimalExact",
    "dec-ran": "decimalRangeMiddle",
    "poi-exa": "pointsExact",
    "poi-ran": "pointsRangeMiddle",
    "ord": "order",
}

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_selection_criteria_number_weight(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse selection criteria number weight (BT-7531) from XML content.

    For each lot's selection criteria, creates/updates corresponding SelectionCriterion
    objects in the lot's selectionCriteria.criteria array with number weights.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with selection criteria or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]

                selection_criteria = lot.xpath(
                    "cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
                    "efext:EformsExtension/efac:SelectionCriteria",
                    namespaces=NAMESPACES,
                )

                if selection_criteria:
                    lot_data = {
                        "id": lot_id,
                        "selectionCriteria": {"criteria": []},
                    }

                    for criterion in selection_criteria:
                        # Check if criterion is used
                        usage = criterion.xpath(
                            "cbc:CalculationExpressionCode[@listName='usage']/text()",
                            namespaces=NAMESPACES,
                        )
                        if usage and usage[0] != "used":
                            continue

                        weights = criterion.xpath(
                            "efac:CriterionParameter[efbc:ParameterCode/@listName='number-weight']"
                            "/efbc:ParameterCode/text()",
                            namespaces=NAMESPACES,
                        )

                        if weights:
                            criterion_data = {
                                "numbers": [
                                    {"weight": WEIGHT_MAPPING.get(w, w)}
                                    for w in weights
                                    if w.strip()
                                ]
                            }
                            if criterion_data["numbers"]:
                                lot_data["selectionCriteria"]["criteria"].append(
                                    criterion_data
                                )

                    if lot_data["selectionCriteria"]["criteria"]:
                        result["tender"]["lots"].append(lot_data)

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot data: %s", e)
                continue

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing selection criteria number weights")
        return None

    return None


def merge_selection_criteria_number_weight(
    release_json: dict[str, Any], number_weight_data: dict[str, Any] | None
) -> None:
    """
    Merge selection criteria number weights into the release JSON.

    Updates or creates selection criteria with number weights for each lot.
    Removes selection criteria from lots where criteria are not used.

    Args:
        release_json: The target release JSON to update
        number_weight_data: The source data containing number weights to merge

    Returns:
        None
    """
    if not number_weight_data:
        # If there's no valid criteria data, make sure no selection criteria exist
        if "tender" in release_json and "lots" in release_json["tender"]:
            for lot in release_json["tender"]["lots"]:
                # Remove any selection criteria from lots when criteria are unused
                lot.pop("selectionCriteria", None)
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    # Create a set of lot IDs that have valid selection criteria
    valid_lot_ids = {lot["id"] for lot in number_weight_data["tender"]["lots"]}

    # Only merge selection criteria for lots that have valid criteria
    for new_lot in number_weight_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            # Update selection criteria for lots with valid criteria
            existing_lot["selectionCriteria"] = new_lot["selectionCriteria"]
        else:
            existing_lots.append(new_lot)

    # Remove selection criteria from lots that don't have valid criteria
    for lot in existing_lots:
        if lot["id"] not in valid_lot_ids:
            lot.pop("selectionCriteria", None)

    logger.info(
        "Merged selection criteria number weight data for %d lots",
        len(number_weight_data["tender"]["lots"]),
    )
