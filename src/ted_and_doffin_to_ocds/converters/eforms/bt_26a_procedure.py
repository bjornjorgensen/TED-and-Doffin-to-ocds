import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_classification_type_procedure(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse classification schemes from procedure XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing items with classification schemes,
                                 or None if no valid data is found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Get classification codes and their schemes
    classification_elements = root.xpath(
        "/*/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode",
        namespaces=namespaces,
    )

    if classification_elements:
        item = {"id": "1", "additionalClassifications": []}

        # Track unique combinations of scheme and code
        added_classifications = set()
        for element in classification_elements:
            list_name = element.get("listName")
            code_value = element.text

            scheme = list_name.upper() if list_name else None

            # Only add if we have both scheme and code, and this combination is unique
            if (
                scheme
                and code_value
                and (scheme, code_value) not in added_classifications
            ):
                item["additionalClassifications"].append(
                    {"scheme": scheme, "id": code_value}
                )
                added_classifications.add((scheme, code_value))

        if item["additionalClassifications"]:
            return {"tender": {"items": [item]}}

    return None


def merge_classification_type_procedure(
    release_json: dict[str, Any], classification_type_data: dict[str, Any] | None
) -> None:
    """Merge classification scheme data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        classification_type_data (Optional[Dict[str, Any]]): Item data containing schemes to merge

    """
    if not classification_type_data:
        return

    tender = release_json.setdefault("tender", {})
    items = tender.setdefault("items", [])

    new_item = classification_type_data["tender"]["items"][0]
    existing_item = next((item for item in items if item["id"] == new_item["id"]), None)

    if existing_item:
        existing_classifications = existing_item.setdefault(
            "additionalClassifications", []
        )
        # Track existing schemes
        existing_schemes = {
            ec.get("scheme") for ec in existing_classifications if "scheme" in ec
        }

        # Update or add classifications
        for new_classification in new_item["additionalClassifications"]:
            scheme = new_classification.get("scheme")
            if scheme and scheme not in existing_schemes:
                # Try to find matching ID
                matched = False
                for ec in existing_classifications:
                    if "id" in ec and "scheme" not in ec:
                        ec["scheme"] = scheme
                        matched = True
                        break
                if not matched:
                    existing_classifications.append(new_classification)
    else:
        items.append(new_item)
