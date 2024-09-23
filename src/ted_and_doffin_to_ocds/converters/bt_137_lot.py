# converters/bt_137_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_purpose_lot_identifier(xml_content):
    """
    Parse the XML content to extract the purpose lot identifier for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed purpose lot identifier data.
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
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        lot_data = {"id": lot_id}
        result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_purpose_lot_identifier(release_json, purpose_lot_identifier_data):
    """
    Merge the parsed purpose lot identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        purpose_lot_identifier_data (dict): The parsed purpose lot identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not purpose_lot_identifier_data:
        logger.warning("No purpose lot identifier data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in purpose_lot_identifier_data["tender"]["lots"]:
        if not any(lot["id"] == new_lot["id"] for lot in existing_lots):
            existing_lots.append(new_lot)

    logger.info(
        f"Merged purpose lot identifier data for {len(purpose_lot_identifier_data['tender']['lots'])} lots",
    )
