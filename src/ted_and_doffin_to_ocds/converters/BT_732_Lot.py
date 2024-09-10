# converters/BT_732_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_security_clearance_description(xml_content):
    """
    Parse the XML content to extract security clearance description for lots.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed security clearance description data for lots.
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        security_clearance = lot.xpath(
            "cac:TenderingTerms/cac:SecurityClearanceTerm/cbc:Description/text()",
            namespaces=namespaces,
        )

        if security_clearance:
            lot_data = {
                "id": lot_id,
                "otherRequirements": {
                    "securityClearance": security_clearance[0].strip()
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_security_clearance_description(
    release_json, lot_security_clearance_description_data
):
    """
    Merge the parsed security clearance description data for lots into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_security_clearance_description_data (dict): The parsed security clearance description data for lots to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_security_clearance_description_data:
        logger.warning("No lot security clearance description data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "lots" not in release_json["tender"]:
        release_json["tender"]["lots"] = []

    for new_lot in lot_security_clearance_description_data["tender"]["lots"]:
        existing_lot = next(
            (
                lot
                for lot in release_json["tender"]["lots"]
                if lot["id"] == new_lot["id"]
            ),
            None,
        )
        if existing_lot:
            if "otherRequirements" not in existing_lot:
                existing_lot["otherRequirements"] = {}
            existing_lot["otherRequirements"]["securityClearance"] = new_lot[
                "otherRequirements"
            ]["securityClearance"]
        else:
            release_json["tender"]["lots"].append(new_lot)

    logger.info(
        f"Merged security clearance description data for {len(lot_security_clearance_description_data['tender']['lots'])} lots"
    )
