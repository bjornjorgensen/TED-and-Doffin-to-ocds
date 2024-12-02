# bt_26m_part.py

from typing import Any

from lxml import etree


def parse_main_classification_type_part(xml_content: str | bytes) -> dict[str, Any]:
    """
    Parse the classification type (e.g. CPV) from procurement project parts in XML content.

    Args:
        xml_content: XML string or bytes containing procurement project parts

    Returns:
        Dict containing tender items with classification schemes

    Example:
        {
            "tender": {
                "items": [
                    {
                        "id": "1",
                        "classification": {"scheme": "CPV"}
                    }
                ]
            }
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"items": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
        namespaces=namespaces,
    )

    for part in parts:
        classification = part.xpath(
            "cac:ProcurementProject/cac:MainCommodityClassification/cbc:ItemClassificationCode",
            namespaces=namespaces,
        )

        if classification:
            scheme = classification[0].get("listName", "").upper()
            if scheme:
                item = {
                    "id": str(len(result["tender"]["items"]) + 1),
                    "classification": {"scheme": scheme},
                }
                result["tender"]["items"].append(item)

    return result


def merge_main_classification_type_part(
    release_json: dict[str, Any], classification_type_data: dict[str, Any]
) -> None:
    """
    Merge classification type data into existing release JSON.

    Args:
        release_json: Target release JSON to merge into
        classification_type_data: Source classification data to merge from

    Returns:
        None. Modifies release_json in place.
    """
    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in classification_type_data["tender"]["items"]:
        existing_item = next(
            (item for item in existing_items if item["id"] == new_item["id"]),
            None,
        )

        if existing_item:
            existing_item["classification"] = new_item["classification"]
        else:
            existing_items.append(new_item)
