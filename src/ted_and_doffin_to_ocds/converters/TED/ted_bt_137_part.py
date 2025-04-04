import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_identifier(xml_content: str | bytes) -> dict | None:
    r"""Parse the part identifier from TED XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing part information

    Returns:
        Optional[Dict]: Dictionary containing tender information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "id": str  # Part identifier
            }
        }

    Note:
        According to TED guidance, if a lot/part number isn't specified, it defaults to '1'.
        The part identifier must follow the pattern ^PAR-\d{4}$ (PAR- followed by exactly 4 digits).
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    # TED XML doesn't use namespaces in the same way as eForms
    # Try to extract part/lot numbers from various possible paths
    part_paths = [
        "//TED_EXPORT/FORM_SECTION/F01_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F03_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F04_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/PRIOR_INFORMATION_DEFENCE/FD_PRIOR_INFORMATION_DEFENCE/OBJECT_WORKS_SUPPLIES_SERVICES_PRIOR_INFORMATION/QUANTITY_SCOPE_WORKS_DEFENCE/F16_DIVISION_INTO_LOTS/F16_DIV_INTO_LOT_YES/LOT_PRIOR_INFORMATION/LOT_NUMBER",
        "//TED_EXPORT/FORM_SECTION/F21_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
        "//TED_EXPORT/FORM_SECTION/F22_2014/OBJECT_CONTRACT/OBJECT_DESCR/LOT_NO",
    ]

    part_ids = []

    for path in part_paths:
        nodes = root.xpath(path)
        if nodes:
            part_ids.extend(
                [node.text for node in nodes if node.text and node.text.strip()]
            )

    # If no part numbers found, add default part '1' according to TED guidance
    if not part_ids:
        part_ids = ["1"]

    # Format the part ID to match the required pattern PAR-XXXX
    if part_ids:
        part_id = part_ids[0].strip()

        # If the part_id already follows the exact PAR-XXXX pattern, use it as is
        if part_id.startswith("PAR-") and len(part_id) == 8 and part_id[4:].isdigit():
            formatted_part_id = part_id
        else:
            # Otherwise, format it to match the required pattern
            try:
                # Try to convert to integer if it's a number
                int_part_id = int(part_id)
                formatted_part_id = f"PAR-{int_part_id:04d}"
            except ValueError:
                # If not convertible to int, use the default
                logger.warning(
                    "Invalid part ID format '%s', using default PAR-0001", part_id
                )
                formatted_part_id = "PAR-0001"

        return {"tender": {"id": formatted_part_id}}

    return None


def merge_part_identifier(release_json: dict, part_data: dict | None) -> None:
    """Merge part identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        part_data (Optional[Dict]): The source data containing tender part ID
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by setting the
        tender.id field.
    """
    if not part_data:
        return

    tender = release_json.setdefault("tender", {})
    tender["id"] = part_data["tender"]["id"]
