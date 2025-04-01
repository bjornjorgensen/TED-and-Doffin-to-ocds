import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_title(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parses the lot title (BT-21-Lot) from TED XML content.

    The function searches for lot titles within various potential locations
    in the TED XML structure based on different form types (F01, F02, F04, F05, F15, F17, F21-F25).
    It extracts the title for each lot found and assigns a sequential ID (lot-1, lot-2, ...).

    Args:
        xml_content: The TED XML content as a string or bytes.

    Returns:
        A dictionary containing the parsed lot titles structured according to OCDS
        under `tender.lots`, or None if no lots are found.
        Example: {'tender': {'lots': [{'id': 'lot-1', 'title': 'Lot Title 1'}]}}
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {}

    result = {"tender": {"lots": []}}

    # Updated XPath patterns based on the provided context
    lot_xpath_patterns = [
        "//TED_EXPORT/FORM_SECTION/F01_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F02_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F04_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F05_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F15_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/OBJECT_CONTRACT_INFORMATION_DEFENCE/DESCRIPTION_CONTRACT_INFORMATION_DEFENCE/F17_DIVISION_INTO_LOTS/F17_DIV_INTO_LOT_YES/F17_ANNEX_B",
        "//TED_EXPORT/FORM_SECTION/F21_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F22_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F23_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F24_2014/OBJECT_CONTRACT/OBJECT_DESCR",
        "//TED_EXPORT/FORM_SECTION/F25_2014/OBJECT_CONTRACT/OBJECT_DESCR",
    ]

    found_lots = False
    for xpath_pattern in lot_xpath_patterns:
        lots = root.xpath(xpath_pattern, namespaces=namespaces)

        if not lots:
            continue

        found_lots = True
        for i, lot in enumerate(lots):
            lot_id = f"lot-{i + 1}"

            # Use specific title paths based on the parent element
            if "F17_ANNEX_B" in xpath_pattern:
                title_elements = lot.xpath("LOT_TITLE/text()", namespaces=namespaces)
            else:
                title_elements = lot.xpath("TITLE/text()", namespaces=namespaces)

            if title_elements:
                existing_lot = next(
                    (
                        lot_item
                        for lot_item in result["tender"]["lots"]
                        if lot_item["id"] == lot_id
                    ),
                    None,
                )
                if not existing_lot:
                    result["tender"]["lots"].append(
                        {"id": lot_id, "title": title_elements[0]}
                    )

        if found_lots:
            break

    return result if result["tender"]["lots"] else None


def merge_lot_title(
    release_json: dict[str, Any], lot_title_data: dict[str, Any] | None
) -> None:
    """
    Merges the parsed lot title data into an existing OCDS release JSON object.

    It iterates through the lots found in `lot_title_data` and updates or adds
    them to the `tender.lots` array in the `release_json`. If a lot with the
    same ID already exists, its title is updated. Otherwise, the new lot is appended.

    Args:
        release_json: The OCDS release JSON object to merge into.
        lot_title_data: The dictionary containing parsed lot titles, as returned
                        by `parse_lot_title`.
    """
    if not lot_title_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_title_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["title"] = new_lot["title"]
        else:
            existing_lots.append(new_lot)
