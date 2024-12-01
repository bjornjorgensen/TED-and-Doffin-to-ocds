# converters/bt_263_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_classification_code_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse the XML content to extract additional classification codes for each part.

    Processes BT-263-Part field which contains additional codes that characterize the purchase.
    XML path: /*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/
             cac:AdditionalCommodityClassification/cbc:ItemClassificationCode

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

    # Check for parts with additional classification codes
    parts_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
    parts = root.xpath(parts_xpath, namespaces=namespaces)
    if not parts:
        logger.info("No parts found with additional classification codes")
        return None

    result = {"tender": {"items": []}}

    for part in parts:
        classifications = part.xpath(
            "cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode",
            namespaces=namespaces,
        )

        if classifications:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "additionalClassifications": [],
            }

            added_codes = set()
            for classification in classifications:
                scheme = classification.get("listName", "").upper()
                code = classification.text
                if scheme and code:
                    code_key = f"{scheme}:{code}"
                    if code_key not in added_codes:
                        item["additionalClassifications"].append(
                            {"scheme": scheme, "id": code}
                        )
                        added_codes.add(code_key)

            if item["additionalClassifications"]:
                result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_additional_classification_code_part(
    release_json: dict[str, Any],
    additional_classification_data: dict[str, Any] | None,
) -> None:
    """
    Merge additional classification code data for parts into the main OCDS release JSON.

    Updates existing items with additional classifications or creates new items
    if they don't exist. Handles deduplication of classification codes.

    Args:
        release_json: The main OCDS release JSON document to update
        additional_classification_data: Parsed classification data to merge,
            in the format returned by parse_additional_classification_code_part()

    Returns:
        None: Updates release_json in-place
    """
    if not additional_classification_data:
        logger.info("No additional classification code data for parts to merge")
        return

    tender = release_json.setdefault("tender", {})
    items = tender.setdefault("items", [])

    for new_item in additional_classification_data["tender"]["items"]:
        existing_item = next(
            (item for item in items if item["id"] == new_item["id"]), None
        )

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

    logger.info(
        "Merged additional classification code data for %d parts",
        len(additional_classification_data["tender"]["items"]),
    )
