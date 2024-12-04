# converters/bt_726_LotsGroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lots_group_sme_suitability(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract SME suitability information for lot groups.

    This function processes XML content to extract whether lot groups are marked as
    suitable for small and medium enterprises (SMEs).

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: A dictionary containing the parsed SME suitability data in the format:
            {
                "tender": {
                    "lotGroups": [
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

    result = {"tender": {"lotGroups": []}}

    lot_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lot_group in lot_groups:
        lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=namespaces)
        sme_suitable = lot_group.xpath(
            "cac:ProcurementProject/cbc:SMESuitableIndicator/text()",
            namespaces=namespaces,
        )

        if lot_group_id and sme_suitable:
            lot_group_data = {
                "id": lot_group_id[0],
                "suitability": {"sme": sme_suitable[0].lower() == "true"},
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_lots_group_sme_suitability(
    release_json: dict, lots_group_sme_suitability_data: dict | None
) -> None:
    """
    Merge the parsed SME suitability data for lot groups into the main OCDS release JSON.

    This function takes SME suitability data and merges it into the main OCDS release JSON.
    For each lot group in the suitability data, it either updates an existing lot group or adds a new one.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated
        lots_group_sme_suitability_data (Optional[Dict]): The parsed SME suitability data for lot groups to be merged.
                                                         If None, the function returns without changes.

    Returns:
        None: The function updates the release_json in-place.

    Note:
        - If lots_group_sme_suitability_data is None, a warning is logged and no changes are made
        - For existing lot groups, suitability.sme value is updated
    """
    if not lots_group_sme_suitability_data:
        logger.warning("No lot group SME suitability data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "lotGroups" not in release_json["tender"]:
        release_json["tender"]["lotGroups"] = []

    for new_lot_group in lots_group_sme_suitability_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (
                lg
                for lg in release_json["tender"]["lotGroups"]
                if lg["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            if "suitability" not in existing_lot_group:
                existing_lot_group["suitability"] = {}
            existing_lot_group["suitability"]["sme"] = new_lot_group["suitability"][
                "sme"
            ]
        else:
            release_json["tender"]["lotGroups"].append(new_lot_group)

    logger.info(
        "Merged SME suitability data for %d lot groups",
        len(lots_group_sme_suitability_data["tender"]["lotGroups"]),
    )
