import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lots_group_internal_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse internal identifiers for lot groups from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing lot groups data with internal identifiers,
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

    lot_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lot_group in lot_groups:
        lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        internal_id = lot_group.xpath(
            "cac:ProcurementProject/cbc:ID[@schemeName='InternalID']/text()",
            namespaces=namespaces,
        )

        if internal_id:
            result["tender"]["lotGroups"].append(
                {
                    "id": lot_group_id,
                    "identifiers": [{"id": internal_id[0], "scheme": "internal"}],
                },
            )

    return result if result["tender"]["lotGroups"] else None


def merge_lots_group_internal_identifier(
    release_json: dict[str, Any],
    lots_group_internal_identifier_data: dict[str, Any] | None,
) -> None:
    """Merge lot group internal identifier data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        lots_group_internal_identifier_data (Optional[Dict[str, Any]]): Lot group data containing internal identifiers to merge

    """
    if not lots_group_internal_identifier_data:
        logger.warning("No lots group internal identifier data to merge")
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault(
        "lotGroups",
        [],
    )

    for new_lot_group in lots_group_internal_identifier_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (
                group
                for group in existing_lot_groups
                if group["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            existing_lot_group["identifiers"] = new_lot_group["identifiers"]
        else:
            existing_lot_groups.append(new_lot_group)
