from typing import Any

from lxml import etree


def parse_main_classification_code_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse the XML content to extract main classification codes for each part.

    Processes BT-262-Part field which contains the main classification code.
    XML path: /*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/
             cac:MainCommodityClassification/cbc:ItemClassificationCode

    Args:
        xml_content: XML content as string or bytes to parse

    Returns:
        Dictionary containing tender items with main classifications if found,
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

    result = {"tender": {"items": []}}

    # Process each part
    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces
    )
    for part in parts:
        classification = part.xpath(
            "cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode/text()",
            namespaces=namespaces,
        )

        if classification:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "classification": {"id": classification[0]},
            }
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_main_classification_code_part(
    release_json: dict[str, Any], classification_code_data: dict[str, Any] | None
) -> None:
    """
    Merge main classification code data into the main OCDS release JSON.

    Updates existing items with main classification codes.

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

    for new_item in classification_code_data["tender"]["items"]:
        existing_item = next(
            (item for item in items if item["id"] == new_item["id"]), None
        )

        if existing_item:
            # Update or create classification
            existing_item.setdefault("classification", {}).update(
                new_item["classification"]
            )
        else:
            items.append(new_item)
