# converters/bt_263_lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_classification_code(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse classification codes from lot XML content.

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

    # Check if any additional classification codes exist
    xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode"
    if not root.xpath(xpath, namespaces=namespaces):
        logger.info("No additional classification code data found.")
        return None

    result = {"tender": {"items": []}}

    # Update parsing to only capture classification IDs
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        codes = lot.xpath(
            "cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode/text()",
            namespaces=namespaces,
        )

        if codes:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "additionalClassifications": [],
                "relatedLot": lot_id,
            }

            # Add unique classification IDs
            added_codes = set()
            for code in codes:
                if code not in added_codes:
                    item["additionalClassifications"].append({"id": code})
                    added_codes.add(code)

            if item["additionalClassifications"]:
                result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def _create_classification(
    scheme: str | None = None, id_value: str | None = None
) -> dict[str, str]:
    """Create a standardized classification dictionary with consistent field order."""
    result = {}
    if scheme:
        result["scheme"] = scheme
    if id_value:
        result["id"] = id_value
    return result if result else None


def merge_additional_classification_code(
    release_json: dict[str, Any],
    additional_classification_data: dict[str, Any] | None,
) -> None:
    """Merge classification code data into the release JSON."""
    if not additional_classification_data:
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in additional_classification_data["tender"]["items"]:
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
            # Get existing scheme if available
            existing_scheme = next(
                (c["scheme"] for c in existing_classifications if "scheme" in c),
                None,
            )

            # Create new properly formatted classifications
            updated_classifications = []
            seen = set()

            # Process existing classifications first
            for ec in existing_classifications:
                scheme = ec.get("scheme") or existing_scheme
                id_value = ec.get("id")
                if scheme and id_value:
                    key = f"{scheme}:{id_value}"
                    if key not in seen:
                        c = _create_classification(scheme, id_value)
                        if c:
                            updated_classifications.append(c)
                            seen.add(key)

            # Add new classifications
            for nc in new_item["additionalClassifications"]:
                scheme = nc.get("scheme") or existing_scheme
                id_value = nc.get("id")
                if scheme and id_value:
                    key = f"{scheme}:{id_value}"
                    if key not in seen:
                        c = _create_classification(scheme, id_value)
                        if c:
                            updated_classifications.append(c)
                            seen.add(key)

            existing_item["additionalClassifications"] = updated_classifications
        else:
            existing_items.append(new_item)
