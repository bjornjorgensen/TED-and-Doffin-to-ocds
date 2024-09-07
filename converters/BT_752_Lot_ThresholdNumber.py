# converters/BT_752_Lot_ThresholdNumber.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_selection_criteria_threshold_number(xml_content):
    """
    Parse the XML content to extract the selection criteria threshold number for each lot.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed selection criteria threshold number data.
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
        selection_criteria = lot.xpath(
            ".//efac:SelectionCriteria", namespaces=namespaces
        )

        lot_data = {"id": lot_id, "selectionCriteria": {"criteria": []}}

        for criterion in selection_criteria:
            usage = criterion.xpath(
                "cbc:CalculationExpressionCode[@listName='usage']/text()",
                namespaces=namespaces,
            )
            if usage and usage[0] != "used":
                continue

            threshold_number = criterion.xpath(
                "efac:CriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efbc:ParameterNumeric/text()",
                namespaces=namespaces,
            )

            if threshold_number:
                criterion_data = {"numbers": [{"number": float(threshold_number[0])}]}
                lot_data["selectionCriteria"]["criteria"].append(criterion_data)

        if lot_data["selectionCriteria"]["criteria"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_selection_criteria_threshold_number(release_json, threshold_number_data):
    """
    Merge the parsed selection criteria threshold number data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        threshold_number_data (dict): The parsed selection criteria threshold number data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not threshold_number_data:
        logger.warning("No selection criteria threshold number data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in threshold_number_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_criteria = existing_lot.setdefault(
                "selectionCriteria", {}
            ).setdefault("criteria", [])
            for new_criterion in new_lot["selectionCriteria"]["criteria"]:
                existing_criterion = next(
                    (c for c in existing_criteria if "numbers" not in c), None
                )
                if existing_criterion:
                    existing_criterion["numbers"] = new_criterion["numbers"]
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged selection criteria threshold number data for {len(threshold_number_data['tender']['lots'])} lots"
    )
