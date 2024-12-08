# converters/bt_137_LotsGroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lots_group_identifier(xml_content: str | bytes) -> dict | None:
    """Parse the lot group identifiers from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot group information

    Returns:
        Optional[Dict]: Dictionary containing tender lot group information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lotGroups": [
                    {
                        "id": str
                    }
                ]
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

    group_ids = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cbc:ID/text()",
        namespaces=namespaces,
    )

    if group_ids:
        return {"tender": {"lotGroups": [{"id": group_id} for group_id in group_ids]}}

    return None


def merge_lots_group_identifier(
    release_json: dict, lots_group_data: dict | None
) -> None:
    """Merge lot group identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        lots_group_data (Optional[Dict]): The source data containing tender lot groups
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding new lot groups to
        tender.lotGroups only if they don't already exist.

    """
    if not lots_group_data:
        return

    existing_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
    existing_group_ids = {group["id"] for group in existing_groups}

    # Only add groups that don't already exist
    new_groups = [
        group
        for group in lots_group_data["tender"]["lotGroups"]
        if group["id"] not in existing_group_ids
    ]
    existing_groups.extend(new_groups)
