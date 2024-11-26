# converters/bt_7531_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

weight_mapping = {
    "per-exa": "percentageExact",
    "per-ran": "percentageRangeMiddle",
    "dec-exa": "decimalExact",
    "dec-ran": "decimalRangeMiddle",
    "poi-exa": "pointsExact",
    "poi-ran": "pointsRangeMiddle",
    "ord": "order",
}


def parse_selection_criteria_number_weight(xml_content):
    """
    Parse the XML content to extract the selection criteria number weight for each lot.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed selection criteria number weight data.
        None: If no relevant data is found.
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

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']"
    lots = root.xpath(xpath_query, namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        # Use exact path as specified in requirements
        selection_criteria = lot.xpath(
            "cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:SelectionCriteria",
            namespaces=namespaces,
        )

        lot_data = {"id": lot_id, "selectionCriteria": {"criteria": []}}

        for criterion in selection_criteria:
            usage = criterion.xpath(
                "cbc:CalculationExpressionCode[@listName='usage']/text()",
                namespaces=namespaces,
            )
            if usage and usage[0] != "used":
                continue

            criterion_parameters = criterion.xpath(
                "efac:CriterionParameter[efbc:ParameterCode/@listName='number-weight']",
                namespaces=namespaces,
            )

            for parameter in criterion_parameters:
                weight_code = parameter.xpath(
                    "efbc:ParameterCode/text()",
                    namespaces=namespaces,
                )

                if weight_code:
                    weight = weight_mapping.get(weight_code[0], weight_code[0])
                    criterion_data = {"numbers": [{"weight": weight}]}
                    lot_data["selectionCriteria"]["criteria"].append(criterion_data)

        if lot_data["selectionCriteria"]["criteria"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_selection_criteria_number_weight(release_json, number_weight_data):
    """
    Merge the parsed selection criteria number weight data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        number_weight_data (dict): The parsed selection criteria number weight data to be merged.

    Returns:
        None: The function updates the release_json in-place.
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
