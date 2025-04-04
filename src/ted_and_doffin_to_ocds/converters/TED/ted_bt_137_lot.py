import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_purpose_lot_identifier(xml_content: str | bytes) -> dict | None:
    """Parse the lot identifiers from TED XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot information

    Returns:
        Optional[Dict]: Dictionary containing tender lot information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lots": [
                    {
                        "id": str
                    }
                ]
            }
        }

    Note:
        According to TED guidance, if a lot number isn't specified, it defaults to '1'.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    # TED XML doesn't use namespaces in the same way as eForms
    # Try to extract lot numbers from various possible paths
    lot_paths = [
        "//TED_EXPORT/FORM_SECTION/F01_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F02_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F04_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F05_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F15_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F20_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F21_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F22_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F23_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F24_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F25_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
    ]

    lot_ids = []

    for path in lot_paths:
        nodes = root.xpath(path)
        if nodes:
            lot_ids.extend(
                [node.text for node in nodes if node.text and node.text.strip()]
            )

    # If no lot numbers found, add default lot '1' according to TED guidance
    if not lot_ids:
        lot_ids = ["1"]

    # Create the LOT-XXXX format from the lot numbers if needed
    formatted_lot_ids = []
    for lot_id in lot_ids:
        # If the lot_id already follows the LOT-XXXX pattern, use it as is
        if lot_id.startswith("LOT-") and len(lot_id) == 8:
            formatted_lot_ids.append(lot_id)
        else:
            # Otherwise, try to format it (assuming lot_id is a number)
            try:
                int_lot_id = int(lot_id)
                formatted_lot_ids.append(f"LOT-{int_lot_id:04d}")
            except ValueError:
                # If not convertible to int, use as is
                formatted_lot_ids.append(lot_id)

    if formatted_lot_ids:
        return {"tender": {"lots": [{"id": lot_id} for lot_id in formatted_lot_ids]}}

    return None


def merge_purpose_lot_identifier(
    release_json: dict, purpose_lot_identifier_data: dict | None
) -> None:
    """Merge lot identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        purpose_lot_identifier_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding new lots to tender.lots
        only if they don't already exist.
    """
    if not purpose_lot_identifier_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    existing_lot_ids = {lot["id"] for lot in existing_lots}

    # Only add lots that don't already exist
    new_lots = [
        lot
        for lot in purpose_lot_identifier_data["tender"]["lots"]
        if lot["id"] not in existing_lot_ids
    ]
    existing_lots.extend(new_lots)
