import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-163: Concession Value Description
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F23_2014/AWARD_CONTRACT/AWARDED_CONTRACT/INFO_ADD_VALUE
# - TED_EXPORT/FORM_SECTION/F25_2014/AWARD_CONTRACT/AWARDED_CONTRACT/INFO_ADD_VALUE
# - TED_EXPORT/FORM_SECTION/F25_2014/OBJECT_CONTRACT/CALCULATION_METHOD
# OCDS Mapping: awards[].valueCalculationMethod


def _process_award_contract(
    root: etree._Element, form_name: str, xpath_path: str
) -> list[dict[str, Any]]:
    """Process award contract sections to extract value descriptions.

    Args:
        root: XML root element
        form_name: Form name to check
        xpath_path: XPath to check for value description

    Returns:
        List of award dictionaries with value descriptions
    """
    awards = []
    sections = root.xpath(f"FORM_SECTION/{form_name}/AWARD_CONTRACT")

    for i, section in enumerate(sections):
        # Get concession value description
        value_desc_nodes = section.xpath(f"{xpath_path.split('/', 1)[1]}/text()")
        if not value_desc_nodes:
            continue

        value_desc = value_desc_nodes[0].strip()
        if not value_desc:
            continue

        # Get lot ID to link to award
        lot_id = section.xpath("LOT_NO/text()")
        lot_id = lot_id[0].strip() if lot_id else None

        # Generate award ID
        award_id = f"RES-{i + 1:04d}"

        award = {
            "id": award_id,
            "valueCalculationMethod": value_desc,
        }

        # Add relatedLots if lot_id exists
        if lot_id:
            award["relatedLots"] = [lot_id]

        awards.append(award)
        logger.info(
            "Found award %s with concession value description",
            award_id,
        )

    return awards


def _process_object_contract(
    root: etree._Element, form_name: str, xpath_path: str
) -> list[dict[str, Any]]:
    """Process object contract sections to extract value descriptions.

    Args:
        root: XML root element
        form_name: Form name to check
        xpath_path: XPath to check for value description

    Returns:
        List of award dictionaries with value descriptions
    """
    awards = []
    calc_method_nodes = root.xpath(f"FORM_SECTION/{form_name}/{xpath_path}/text()")

    if calc_method_nodes and calc_method_nodes[0].strip():
        value_desc = calc_method_nodes[0].strip()
        # For object contract, apply to all awards
        lots = root.xpath(f"FORM_SECTION/{form_name}/OBJECT_CONTRACT/LOT")

        for i, lot in enumerate(lots):
            lot_id = lot.xpath("LOT_NO/text()")
            lot_id = lot_id[0].strip() if lot_id else None

            award_id = f"RES-{i + 1:04d}"

            award = {
                "id": award_id,
                "valueCalculationMethod": value_desc,
            }

            if lot_id:
                award["relatedLots"] = [lot_id]

            awards.append(award)
            logger.info(
                "Added concession value description to award %s",
                award_id,
            )

    return awards


def parse_concession_value_description(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses the concession value description from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing award information,
        or None if no data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"awards": []}

        # Forms to check for different XPaths
        forms_to_check = {
            "F23_2014": "AWARD_CONTRACT/AWARDED_CONTRACT/INFO_ADD_VALUE",
            "F25_2014": [
                "AWARD_CONTRACT/AWARDED_CONTRACT/INFO_ADD_VALUE",
                "OBJECT_CONTRACT/CALCULATION_METHOD",
            ],
        }

        for form_name, xpath_list in forms_to_check.items():
            paths_to_check = (
                xpath_list if isinstance(xpath_list, list) else [xpath_list]
            )

            for xpath_path in paths_to_check:
                # Get all award contracts or object contracts depending on the path
                if "AWARD_CONTRACT" in xpath_path:
                    awards = _process_award_contract(root, form_name, xpath_path)
                else:
                    awards = _process_object_contract(root, form_name, xpath_path)

                result["awards"].extend(awards)

        return result if result["awards"] else None

    except Exception:
        logger.exception("Error parsing concession value description")
        return None


def merge_concession_value_description(
    release_json: dict[str, Any],
    value_description_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the concession value description data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        value_description_data (Optional[Dict[str, List[Dict[str, Any]]]]):
            The concession value description data to merge.

    Returns:
        None
    """
    if not value_description_data:
        logger.info("No Concession Value Description data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in value_description_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )

        if existing_award:
            existing_award["valueCalculationMethod"] = new_award[
                "valueCalculationMethod"
            ]

            # Merge relatedLots if present
            if "relatedLots" in new_award:
                existing_lots = set(existing_award.get("relatedLots", []))
                existing_lots.update(new_award["relatedLots"])
                existing_award["relatedLots"] = list(existing_lots)
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged Concession Value Description data for %d awards",
        len(value_description_data["awards"]),
    )
