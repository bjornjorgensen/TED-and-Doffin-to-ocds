# converters/bt_752_Lot_WeightNumber.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
}


def parse_selection_criteria_weight_number(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse BT-752: Selection criteria weight numbers for lots.

    These values are mapped to the same SelectionCriterion objects as created for
    BT-40-Lot, BT-750-Lot, BT-7531-Lot, BT-7532-Lot and BT-809-Lot.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "selectionCriteria": {
                                "criteria": [
                                    {
                                        "numbers": [
                                            {
                                                "number": float
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            criteria = lot.xpath(
                ".//efac:SelectionCriteria/efac:CriterionParameter[efbc:ParameterCode/@listName='number-weight']",
                namespaces=NAMESPACES,
            )

            if criteria:
                lot_data = {"id": lot_id, "selectionCriteria": {"criteria": []}}

                for criterion in criteria:
                    weight = criterion.xpath(
                        "efbc:ParameterNumeric/text()", namespaces=NAMESPACES
                    )
                    if weight:
                        try:
                            number = float(weight[0])
                            logger.info(
                                "Found weight number %f for lot %s", number, lot_id
                            )
                            lot_data["selectionCriteria"]["criteria"].append(
                                {"numbers": [{"number": number}]}
                            )
                        except ValueError:
                            logger.warning("Invalid weight number: %s", weight[0])

                if lot_data["selectionCriteria"]["criteria"]:
                    result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing selection criteria weight numbers")
        return None


def merge_selection_criteria_weight_number(
    release_json: dict, weight_data: dict | None
) -> None:
    """
    Merge selection criteria weight number data into the release JSON.

    Updates or adds weight numbers to lot selection criteria.

    Args:
        release_json: Main OCDS release JSON to update
        weight_data: Selection criteria weight data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' selectionCriteria.criteria
    """
    if not weight_data:
        logger.warning("No selection criteria weight number data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in weight_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_criteria = existing_lot.setdefault(
                "selectionCriteria", {}
            ).setdefault("criteria", [])
            for new_criterion in new_lot["selectionCriteria"]["criteria"]:
                # Find first criterion without numbers or create new one
                existing_criterion = next(
                    (c for c in existing_criteria if "numbers" not in c), None
                )
                if existing_criterion:
                    existing_criterion["numbers"] = new_criterion["numbers"]
                else:
                    existing_criteria.append(new_criterion)
        else:
            lots.append(new_lot)

    logger.info(
        "Merged selection criteria weight number data for %d lots",
        len(weight_data["tender"]["lots"]),
    )
