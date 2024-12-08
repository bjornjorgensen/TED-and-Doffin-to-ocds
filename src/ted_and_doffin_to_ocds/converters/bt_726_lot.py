# converters/bt_726_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_sme_suitability(xml_content: str | bytes) -> dict | None:
    """Parse the XML content to extract SME suitability information for lots.

    This function processes XML content to extract whether lots are marked as
    suitable for small and medium enterprises (SMEs).

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: A dictionary containing the parsed SME suitability data in the format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "suitability": {
                                "sme": bool
                            }
                        }
                    ]
                }
            }
            Returns None if no relevant data is found.

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


def merge_lot_sme_suitability(
    release_json: dict, lot_sme_suitability_data: dict | None
) -> None:
    """Merge the parsed SME suitability data into the main OCDS release JSON.

    This function takes SME suitability data and merges it into the main OCDS release JSON.
    For each lot in the suitability data, it either updates an existing lot or adds a new one.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated
        lot_sme_suitability_data (Optional[Dict]): The parsed SME suitability data to be merged.
                                                  If None, the function returns without changes.

    Returns:
        None: The function updates the release_json in-place.

    Note:
        - If lot_sme_suitability_data is None, a warning is logged and no changes are made
        - For existing lots, suitability.sme value is updated

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
