# converters/bt_752_Lot_ThresholdNumber.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_selection_criteria_threshold_number(
    xml_content: str | bytes,
) -> dict | None:
    """Parse BT-752: Selection criteria threshold numbers for lots.

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
                                        "id": str,  # Criterion identifier to match with existing criteria
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
            selection_criteria = lot.xpath(
                ".//cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:SelectionCriteria",
                namespaces=NAMESPACES,
            )

            if not selection_criteria:
                continue

            lot_data = {"id": lot_id, "selectionCriteria": {"criteria": []}}

            for criterion in selection_criteria:
                # No longer skipping criteria marked as "not-used"
                # Get usage for logging purposes only
                usage_code = criterion.xpath(
                    "cbc:CalculationExpressionCode[@listName='usage']/text()",
                    namespaces=NAMESPACES,
                )

                # Extract criterion ID or use a position-based identifier if ID not available
                criterion_id = criterion.xpath("efbc:ID/text()", namespaces=NAMESPACES)
                criterion_id = (
                    criterion_id[0]
                    if criterion_id
                    else f"criterion-{len(lot_data['selectionCriteria']['criteria']) + 1}"
                )

                # Find threshold parameters for this criterion
                threshold_parameters = criterion.xpath(
                    "efac:CriterionParameter[efbc:ParameterCode/@listName='number-threshold']",
                    namespaces=NAMESPACES,
                )

                if not threshold_parameters:
                    continue

                criterion_data = {"id": criterion_id, "numbers": []}

                for param in threshold_parameters:
                    threshold = param.xpath(
                        "efbc:ParameterNumeric/text()", namespaces=NAMESPACES
                    )
                    if threshold:
                        try:
                            number = float(threshold[0])
                            usage_info = (
                                f" (marked as '{usage_code[0]}')" if usage_code else ""
                            )
                            logger.info(
                                "Found threshold number %f for lot %s criterion %s%s",
                                number,
                                lot_id,
                                criterion_id,
                                usage_info,
                            )
                            criterion_data["numbers"].append({"number": number})
                        except ValueError:
                            logger.warning("Invalid threshold number: %s", threshold[0])

                if criterion_data["numbers"]:
                    lot_data["selectionCriteria"]["criteria"].append(criterion_data)

            if lot_data["selectionCriteria"]["criteria"]:
                result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing selection criteria threshold numbers")
        return None


def merge_selection_criteria_threshold_number(
    release_json: dict, threshold_data: dict | None
) -> None:
    """Merge selection criteria threshold number data into the release JSON.

    Updates or adds threshold numbers to lot selection criteria.

    Args:
        release_json: Main OCDS release JSON to update
        threshold_data: Selection criteria threshold data to merge, can be None

    Note:
        - Updates release_json in-place
        - Maps threshold numbers to existing criteria based on criterion ID

    """
    if not threshold_data:
        logger.info("No selection criteria threshold number data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    # Track how many lots and criteria were updated
    updated_lots = 0
    updated_criteria = 0

    for new_lot in threshold_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )

        if not existing_lot:
            # If lot doesn't exist yet, add it with the threshold data
            existing_lots.append(new_lot)
            updated_lots += 1
            updated_criteria += len(new_lot["selectionCriteria"]["criteria"])
            continue

        # Ensure lot has selectionCriteria
        existing_criteria = existing_lot.setdefault("selectionCriteria", {}).setdefault(
            "criteria", []
        )

        for new_criterion in new_lot["selectionCriteria"]["criteria"]:
            criterion_id = new_criterion.get("id")

            # Try to find matching criterion by ID or find one without numbers
            existing_criterion = None

            # First attempt to match by ID if available
            if criterion_id:
                existing_criterion = next(
                    (c for c in existing_criteria if c.get("id") == criterion_id), None
                )

            # If no match by ID and no ID provided, find first criterion without numbers
            if not existing_criterion:
                existing_criterion = next(
                    (c for c in existing_criteria if "numbers" not in c), None
                )

            if existing_criterion:
                # Update existing criterion with numbers
                existing_criterion["numbers"] = new_criterion["numbers"]
                updated_criteria += 1
            else:
                # Add as a new criterion
                existing_criteria.append(new_criterion)
                updated_criteria += 1

        updated_lots += 1

    logger.info(
        "Merged selection criteria threshold number data for %d lots and %d criteria",
        updated_lots,
        updated_criteria,
    )
