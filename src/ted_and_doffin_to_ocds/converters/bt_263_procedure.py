import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_classification_code_procedure(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse the XML content to extract additional classification codes for the procedure.

    Processes BT-263-Procedure field which contains additional codes that characterize the purchase.
    XML path: /*/cac:ProcurementProject/cac:AdditionalCommodityClassification/
             cbc:ItemClassificationCode

    Args:
        xml_content: XML content as string or bytes to parse

    Returns:
        Dictionary containing tender items with additional classifications if found,
        structured as:
        {
            "tender": {
                "items": [
                    {
                        "id": str,
                        "additionalClassifications": [{"id": str}]
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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Check for procedure-level additional classification codes
    codes = root.xpath(
        "/*/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode",
        namespaces=namespaces,
    )

    if not codes:
        logger.info("No additional classification code data found for procedure")
        return None

    result = {"tender": {"items": [{"id": "1", "additionalClassifications": []}]}}

    added_codes = set()  # Track unique combinations
    for code in codes:
        scheme = code.get("listName", "").upper()
        id_value = code.text
        if scheme and id_value:
            code_key = f"{scheme}:{id_value}"
            if code_key not in added_codes:
                result["tender"]["items"][0]["additionalClassifications"].append(
                    {"scheme": scheme, "id": id_value}
                )
                added_codes.add(code_key)

    return result if result["tender"]["items"][0]["additionalClassifications"] else None


def merge_additional_classification_code_procedure(
    release_json: dict[str, Any],
    additional_classification_data: dict[str, Any] | None,
) -> None:
    """
    Merge additional classification code data for procedure into the main OCDS release JSON.

    Updates existing items with additional classifications or creates new items
    if they don't exist. Handles deduplication of classification codes.

    Args:
        release_json: The main OCDS release JSON document to update
        additional_classification_data: Parsed classification data to merge,
            in the format returned by parse_additional_classification_code_procedure()

    Returns:
        None: Updates release_json in-place
    """
    if not additional_classification_data:
        logger.info("No additional classification code data for procedure to merge")
        return

    tender = release_json.setdefault("tender", {})
    items = tender.setdefault("items", [])

    new_item = additional_classification_data["tender"]["items"][0]
    existing_item = next((item for item in items if item["id"] == new_item["id"]), None)

    if existing_item:
        existing_classifications = existing_item.setdefault(
            "additionalClassifications", []
        )
        for new_classification in new_item["additionalClassifications"]:
            # Check for duplicates based on both scheme and id
            is_duplicate = any(
                ec.get("scheme") == new_classification.get("scheme")
                and ec.get("id") == new_classification.get("id")
                for ec in existing_classifications
            )
            if not is_duplicate:
                existing_classifications.append(new_classification)
    else:
        items.append(new_item)

    logger.info(
        "Merged additional classification code data for procedure with %d classifications",
        len(new_item["additionalClassifications"]),
    )
