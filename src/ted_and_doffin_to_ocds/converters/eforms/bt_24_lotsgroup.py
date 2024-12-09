# converters/bt_24_LotsGroup.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lots_group_description(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse descriptions for lot groups from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing lot groups data with descriptions,
                                 or None if no valid data is found

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

    lots_group_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lots_group_element in lots_group_elements:
        lots_group_id = lots_group_element.xpath(
            "cbc:ID/text()",
            namespaces=namespaces,
        )[0]
        description = lots_group_element.xpath(
            "cac:ProcurementProject/cbc:Description/text()",
            namespaces=namespaces,
        )

        if description:
            lot_group = {"id": lots_group_id, "description": description[0]}
            result["tender"]["lotGroups"].append(lot_group)

    return result if result["tender"]["lotGroups"] else None


def merge_lots_group_description(
    release_json: dict[str, Any], lots_group_description_data: dict[str, Any] | None
) -> None:
    """Merge lot group description data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        lots_group_description_data (Optional[Dict[str, Any]]): Lot group data containing descriptions to merge

    """
    if not lots_group_description_data:
        logger.warning("No LotsGroup Description data to merge")
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault(
        "lotGroups",
        [],
    )

    for new_lot_group in lots_group_description_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (
                group
                for group in existing_lot_groups
                if group["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            existing_lot_group["description"] = new_lot_group["description"]
        else:
            existing_lot_groups.append(new_lot_group)

    logger.info(
        "Merged LotsGroup Description data for %(num_lot_groups)d lot groups",
        {"num_lot_groups": len(lots_group_description_data["tender"]["lotGroups"])},
    )
