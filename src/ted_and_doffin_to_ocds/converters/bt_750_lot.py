# converters/bt_750_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_selection_criteria(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse the XML content to extract the selection criteria name and description for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the parsed selection criteria data,
                                 or None if no relevant data is found.
    """
    logger.debug("Starting parse_selection_criteria")
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

    # Get all lots
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    logger.debug("Found %d lots", len(lots))

    # Get root level selection criteria first
    root_selection_criteria = root.xpath(
        "//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:SelectionCriteria",
        namespaces=namespaces,
    )
    logger.debug("Found %d root selection criteria", len(root_selection_criteria))

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        logger.debug("Processing lot with ID: %s", lot_id)

        lot_data = {"id": lot_id, "selectionCriteria": {"criteria": []}}

        # Process root level criteria
        for criterion in root_selection_criteria:
            usage = criterion.xpath(
                "cbc:CalculationExpressionCode[@listName='usage']/text()",
                namespaces=namespaces,
            )
            if usage and usage[0] != "used":
                logger.debug("Skipping root criterion with usage: %s", usage[0])
                continue

            name = criterion.xpath("cbc:Name/text()", namespaces=namespaces)
            description = criterion.xpath(
                "cbc:Description/text()",
                namespaces=namespaces,
            )

            logger.debug("Root criterion name: %s, description: %s", name, description)

            if name or description:
                criterion_data = {}
                if name:
                    criterion_data["title"] = name[0]
                if description:
                    criterion_data["description"] = description[0]

                if name and description:
                    criterion_data["description"] = f"{name[0]}: {description[0]}"

                lot_data["selectionCriteria"]["criteria"].append(criterion_data)
                logger.debug("Added root criterion: %s", criterion_data)

        # Process lot level criteria (BT-750)
        lot_selection_criteria = lot.xpath(
            ".//cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:SelectionCriteria",
            namespaces=namespaces,
        )
        logger.debug("Found %d lot selection criteria", len(lot_selection_criteria))

        for criterion in lot_selection_criteria:
            usage = criterion.xpath(
                "cbc:CalculationExpressionCode[@listName='usage']/text()",
                namespaces=namespaces,
            )
            if usage and usage[0] != "used":
                logger.debug("Skipping lot criterion with usage: %s", usage[0])
                continue

            description_element = criterion.xpath(
                "cbc:Description",
                namespaces=namespaces,
            )
            if description_element:
                description = description_element[0].text
                language_id = description_element[0].get("languageID")
                criterion_data = (
                    {"description": description, "languageID": language_id}
                    if language_id
                    else {"description": description}
                )
                lot_data["selectionCriteria"]["criteria"].append(criterion_data)
                logger.debug("Added lot criterion: %s", criterion_data)

        if lot_data["selectionCriteria"]["criteria"]:
            result["tender"]["lots"].append(lot_data)
            logger.debug("Added lot data: %s", lot_data)

    logger.debug("Finished parse_selection_criteria with result: %s", result)
    return result if result["tender"]["lots"] else None


def merge_selection_criteria(
    release_json: dict[str, Any], selection_criteria_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed selection criteria data into the main OCDS release JSON.

    Args:
        release_json (Dict[str, Any]): The main OCDS release JSON to be updated.
        selection_criteria_data (Optional[Dict[str, Any]]): The parsed selection criteria data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not selection_criteria_data:
        logger.warning("No selection criteria data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in selection_criteria_data["tender"]["lots"]:
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
                    (
                        c
                        for c in existing_criteria
                        if c.get("title") == new_criterion.get("title")
                    ),
                    None,
                )
                if existing_criterion:
                    existing_criterion.update(new_criterion)
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged selection criteria data for %d lots",
        len(selection_criteria_data["tender"]["lots"]),
    )
