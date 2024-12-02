# converters/bt_52_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_successive_reduction_indicator(xml_content: str | bytes) -> dict | None:
    """Parse successive reduction indicator from XML content for lots.

    This function extracts the indicator of whether the procedure will take place in
    successive stages from ProcurementProjectLot elements in the XML.

    Args:
        xml_content: XML string or bytes containing procurement data

    Returns:
        Dict containing OCDS formatted data with lots information, or None if no relevant data found.
        Format:
        {
            "tender": {
                "lots": [{
                    "id": str,
                    "secondStage": {
                        "successiveReduction": bool
                    }
                }]
            }
        }
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

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingProcess/cbc:CandidateReductionConstraintIndicator"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No successive reduction indicator data found. Skipping parse_successive_reduction_indicator."
        )
        return None

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        reduction_indicator = lot_element.xpath(
            "./cac:TenderingProcess/cbc:CandidateReductionConstraintIndicator/text()",
            namespaces=namespaces,
        )

        if reduction_indicator:
            lot_data = {
                "id": lot_id,
                "secondStage": {
                    "successiveReduction": reduction_indicator[0].lower() == "true"
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_successive_reduction_indicator(
    release_json: dict, successive_reduction_data: dict | None
) -> None:
    """Merge successive reduction indicator data into an existing OCDS release.

    Updates the lots in the release_json with successive reduction information.

    Args:
        release_json: The OCDS release to be updated
        successive_reduction_data: Data containing successive reduction information to be merged.
                                 Expected to have the same structure as parse_successive_reduction_indicator output.

    Returns:
        None. Updates release_json in place.
    """
    if not successive_reduction_data:
        logger.info("No Successive Reduction Indicator data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in successive_reduction_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("secondStage", {}).update(new_lot["secondStage"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Successive Reduction Indicator data for %d lots",
        len(successive_reduction_data["tender"]["lots"]),
    )
