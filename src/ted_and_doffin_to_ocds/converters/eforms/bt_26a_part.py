import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_classification_type_part(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse classification schemes for part from XML content.

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

    result = {"tender": {"items": []}}

    # Simplify to handle only schemes
    classification_types = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode/@listName",
        namespaces=namespaces,
    )

    if classification_types:
        item = {
            "id": "1",  # Single item for part
            "additionalClassifications": [],
        }

        # Add only unique schemes
        added_schemes = set()
        for list_name in classification_types:
            scheme = list_name.upper() if list_name else None
            if scheme and scheme not in added_schemes:
                item["additionalClassifications"].append({"scheme": scheme})
                added_schemes.add(scheme)

        if item["additionalClassifications"]:
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_classification_type_part(
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
    existing_items = tender.setdefault("items", [])

    for new_item in classification_type_data["tender"]["items"]:
        existing_item = next(
            (item for item in existing_items if item["id"] == new_item["id"]), None
        )

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
            existing_items.append(new_item)
