from typing import Any

from lxml import etree


def parse_classification_type_procedure(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse the XML content to extract classification types (schemes) for the procedure.

    Processes BT-26(a)-Procedure field which contains classification types.
    XML path: /*/cac:ProcurementProject/cac:AdditionalCommodityClassification/
             cbc:ItemClassificationCode/@listName

    Args:
        xml_content: XML content as string or bytes to parse

    Returns:
        Dictionary containing tender items with classification schemes if found,
        structured as:
        {
            "tender": {
                "items": [
                    {
                        "id": str,
                        "additionalClassifications": [{"scheme": str, "id": str}]
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

    # Check for procedure-level classification codes
    classifications = root.xpath(
        "/*/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode",
        namespaces=namespaces,
    )

    if not classifications:
        return None

    result = {"tender": {"items": [{"id": "1", "additionalClassifications": []}]}}
    added_codes = set()  # Track unique combinations of scheme and id

    for classification in classifications:
        scheme = classification.get("listName", "").upper()
        code = classification.text
        if scheme and code:
            code_key = f"{scheme}:{code}"
            if code_key not in added_codes:
                result["tender"]["items"][0]["additionalClassifications"].append(
                    {"scheme": scheme, "id": code}
                )
                added_codes.add(code_key)

    return result if result["tender"]["items"][0]["additionalClassifications"] else None


def merge_classification_type_procedure(
    release_json: dict[str, Any], classification_type_data: dict[str, Any] | None
) -> None:
    """
    Merge classification type data for procedure into the main OCDS release JSON.

    Updates existing items with classification schemes.

    Args:
        release_json: The main OCDS release JSON document to update
        classification_type_data: Parsed classification type data to merge

    Returns:
        None: Updates release_json in-place
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
        existing_pairs = {
            (ec.get("scheme", ""), ec.get("id", ""))
            for ec in existing_classifications
            if "scheme" in ec and "id" in ec
        }

        for new_classification in new_item["additionalClassifications"]:
            if "scheme" in new_classification and "id" in new_classification:
                pair = (new_classification["scheme"], new_classification["id"])
                if pair not in existing_pairs:
                    existing_classifications.append(new_classification)
                    existing_pairs.add(pair)
    else:
        items.append(new_item)
