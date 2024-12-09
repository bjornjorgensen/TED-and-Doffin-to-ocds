from typing import Any

from lxml import etree


def parse_main_classification_code_procedure(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the XML content to extract main classification code for the procedure.

    Processes BT-262-Procedure field which contains the main classification code.
    XML path: /*/cac:ProcurementProject/cac:MainCommodityClassification/
             cbc:ItemClassificationCode

    Args:
        xml_content: XML content as string or bytes to parse

    Returns:
        Dictionary containing tender items with main classification if found,
        structured as:
        {
            "tender": {
                "items": [
                    {
                        "id": str,
                        "classification": {"id": str}
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

    # Check for procedure-level main classification code
    classification = root.xpath(
        "/*/cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode",
        namespaces=namespaces,
    )

    if not classification or not classification[0].text:
        return None

    return {
        "tender": {
            "items": [
                {
                    "id": "1",
                    "classification": {
                        "scheme": classification[0].get("listName", "CPV").upper(),
                        "id": classification[0].text,
                    },
                }
            ]
        }
    }


def merge_main_classification_code_procedure(
    release_json: dict[str, Any], classification_code_data: dict[str, Any] | None
) -> None:
    """Merge main classification code data into the main OCDS release JSON.

    Updates existing items with main classification code.

    Args:
        release_json: The main OCDS release JSON document to update
        classification_code_data: Parsed classification data to merge

    Returns:
        None: Updates release_json in-place

    """
    if not classification_code_data:
        return

    tender = release_json.setdefault("tender", {})
    items = tender.setdefault("items", [])

    new_item = classification_code_data["tender"]["items"][0]
    existing_item = next((item for item in items if item["id"] == new_item["id"]), None)

    if existing_item:
        # Preserve existing scheme if available
        existing_scheme = existing_item.get("classification", {}).get("scheme")
        new_classification = classification_code_data["tender"]["items"][0][
            "classification"
        ]
        if existing_scheme:
            new_classification["scheme"] = existing_scheme
        existing_item.setdefault("classification", {}).update(new_classification)
    else:
        items.append(new_item)
