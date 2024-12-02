# bt_26a_lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_classification_type(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse classification schemes from lot XML content.

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

    # Process each lot
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        classification_types = lot.xpath(
            "cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode/@listName",
            namespaces=namespaces,
        )

        if classification_types:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "additionalClassifications": [],
                "relatedLot": lot_id,
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


def merge_classification_type(
    release_json: dict[str, Any], classification_type_data: dict[str, Any] | None
) -> None:
    """Merge classification scheme data into the release JSON."""
    if not classification_type_data:
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in classification_type_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item.get("relatedLot") == new_item.get("relatedLot")
                and item.get("id") == new_item.get("id")
            ),
            None,
        )

        if existing_item:
            existing_classifications = existing_item.setdefault(
                "additionalClassifications", []
            )
            # Get scheme from new classification if available
            new_scheme = next(
                (
                    c["scheme"]
                    for c in new_item["additionalClassifications"]
                    if "scheme" in c
                ),
                None,
            )

            # Apply scheme to all existing classifications that don't have one
            if new_scheme:
                for ec in existing_classifications:
                    if "id" in ec and "scheme" not in ec:
                        ec["scheme"] = new_scheme

            # Add any new classifications with scheme
            for nc in new_item["additionalClassifications"]:
                if "scheme" in nc and nc not in existing_classifications:
                    existing_classifications.append(nc)
        else:
            existing_items.append(new_item)
