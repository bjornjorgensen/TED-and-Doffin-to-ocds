# converters/bt_50_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_minimum_candidates(xml_content: str | bytes) -> dict | None:
    """Parse minimum number of candidates from XML content for lots.

    This function extracts the minimum number of candidates to be invited for the second stage
    from ProcurementProjectLot elements in the XML.

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
                        "minimumCandidates": int
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

    # Check if the relevant XPath exists (only in TenderingProcess path)
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingProcess/cac:EconomicOperatorShortList/cbc:MinimumQuantity"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No minimum candidates data found. Skipping parse_minimum_candidates."
        )
        return None

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        # Only use TenderingProcess path
        minimum_quantity = lot_element.xpath(
            "./cac:TenderingProcess/cac:EconomicOperatorShortList/cbc:MinimumQuantity/text()",
            namespaces=namespaces,
        )

        if minimum_quantity:
            lot = {
                "id": lot_id,
                "secondStage": {"minimumCandidates": int(minimum_quantity[0])},
            }
            result["tender"]["lots"].append(lot)

    return result if result["tender"]["lots"] else None


def merge_minimum_candidates(
    release_json: dict, minimum_candidates_data: dict | None
) -> None:
    """Merge minimum candidates data into an existing OCDS release.

    Updates the lots in the release_json with minimum candidates information.

    Args:
        release_json: The OCDS release to be updated
        minimum_candidates_data: Data containing minimum candidates information to be merged.
                               Expected to have the same structure as parse_minimum_candidates output.

    Returns:
        None. Updates release_json in place.

    """
    if not minimum_candidates_data:
        logger.info("No Minimum Candidates data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in minimum_candidates_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("secondStage", {}).update(new_lot["secondStage"])
        else:
            tender_lots.append(new_lot)

    logger.info(
        "Merged Minimum Candidates data for %d lots",
        len(minimum_candidates_data["tender"]["lots"]),
    )
