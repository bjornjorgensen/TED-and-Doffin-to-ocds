# converters/bt_726_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_sme_suitability(xml_content):
    """
    Parse the XML content to extract SME suitability information for lots.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed SME suitability data.
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

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        sme_suitable = lot.xpath(
            "cac:ProcurementProject/cbc:SMESuitableIndicator/text()",
            namespaces=namespaces,
        )

        if lot_id and sme_suitable:
            lot_data = {
                "id": lot_id[0],
                "suitability": {"sme": sme_suitable[0].lower() == "true"},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_sme_suitability(release_json, lot_sme_suitability_data):
    """
    Merge the parsed SME suitability data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_sme_suitability_data (dict): The parsed SME suitability data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_sme_suitability_data:
        logger.warning("No lot SME suitability data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "lots" not in release_json["tender"]:
        release_json["tender"]["lots"] = []

    for new_lot in lot_sme_suitability_data["tender"]["lots"]:
        existing_lot = next(
            (
                lot
                for lot in release_json["tender"]["lots"]
                if lot["id"] == new_lot["id"]
            ),
            None,
        )
        if existing_lot:
            if "suitability" not in existing_lot:
                existing_lot["suitability"] = {}
            existing_lot["suitability"]["sme"] = new_lot["suitability"]["sme"]
        else:
            release_json["tender"]["lots"].append(new_lot)

    logger.info(
        "Merged SME suitability data for %d lots",
        len(lot_sme_suitability_data["tender"]["lots"]),
    )
