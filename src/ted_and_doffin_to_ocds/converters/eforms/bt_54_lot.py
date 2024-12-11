# converters/bt_54_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_options_description(xml_content: str | bytes) -> dict | None:
    """Parse options description from XML content for lots.

    This function extracts the options description from ProcurementProjectLot elements in the XML.

    Args:
        xml_content: XML string or bytes containing procurement data

    Returns:
        Dict containing OCDS formatted data with lots information, or None if no relevant data found.
        Format:
        {
            "tender": {
                "lots": [{
                    "id": str,
                    "options": {
                        "description": str
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
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:ProcurementProject/cac:ContractExtension/cbc:OptionsDescription"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No options description data found. Skipping parse_options_description."
        )
        return None

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot_element.xpath(
            "./cac:ProcurementProject/cac:ContractExtension/cbc:OptionsDescription/text()",
            namespaces=namespaces,
        )

        if description:
            lot_data = {
                "id": lot_id,
                "options": {"description": description[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_options_description(
    release_json: dict, options_description_data: dict | None
) -> None:
    """Merge options description data into an existing OCDS release.

    Updates the lots in the release_json with options description information.

    Args:
        release_json: The OCDS release to be updated
        options_description_data: Data containing options description information to be merged.
                                Expected to have the same structure as parse_options_description output.

    Returns:
        None. Updates release_json in place.

    """
    if not options_description_data:
        logger.warning("No Options Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in options_description_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("options", {}).update(new_lot["options"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Options Description data for %d lots",
        len(options_description_data["tender"]["lots"]),
    )
