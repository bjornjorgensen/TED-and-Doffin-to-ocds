import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_classification_code_procedure(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse classification codes from procedure XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing items with classification IDs,
                                 or None if no valid data is found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Get classification code elements instead of just text
    code_elements = root.xpath(
        "/*/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode",
        namespaces=namespaces,
    )

    if code_elements:
        item = {
            "id": "1",  # Single item for procedure
            "additionalClassifications": [],
        }

        # Add unique classification IDs with schemes
        added_codes = set()
        for element in code_elements:
            code = element.text
            if not code or code in added_codes:
                continue

            classification = {"id": code}

            # Extract listName attribute if present and use it as scheme
            list_name = element.get("listName")
            if list_name:
                # Normalize CPV to uppercase for consistency
                if list_name.lower() == "cpv":
                    classification["scheme"] = "CPV"
                else:
                    classification["scheme"] = list_name

            item["additionalClassifications"].append(classification)
            added_codes.add(code)

        return (
            {"tender": {"items": [item]}} if item["additionalClassifications"] else None
        )

    return None


def merge_additional_classification_code_procedure(
    release_json: dict[str, Any],
    additional_classification_data: dict[str, Any] | None,
) -> None:
    """Merge classification code data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        additional_classification_data (Optional[Dict[str, Any]]): Item data containing IDs to merge

    """
    if not additional_classification_data:
        return

    tender = release_json.setdefault("tender", {})
    items = tender.setdefault("items", [])

    new_item = additional_classification_data["tender"]["items"][0]
    existing_item = next((item for item in items if item["id"] == new_item["id"]), None)

    if existing_item:
        existing_classifications = existing_item.setdefault(
            "additionalClassifications", []
        )
        # Track existing IDs
        existing_ids = {ec.get("id") for ec in existing_classifications if "id" in ec}

        # Update or add classifications
        for new_classification in new_item["additionalClassifications"]:
            id_value = new_classification.get("id")
            if id_value and id_value not in existing_ids:
                # Try to find matching scheme
                matched = False
                for ec in existing_classifications:
                    if "scheme" in ec and "id" not in ec:
                        ec["id"] = id_value
                        matched = True
                        break
                if not matched:
                    existing_classifications.append(new_classification)
    else:
        items.append(new_item)

    logger.info(
        "Merged additional classification code data for procedure with %d classifications",
        len(new_item["additionalClassifications"]),
    )
