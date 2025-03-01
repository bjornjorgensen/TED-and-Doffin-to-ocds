# converters/bt_531_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_additional_nature(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the additional nature (BT-531) for procurement project parts from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed part additional nature data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "additionalProcurementCategories": ["nature1", "nature2"]
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

    result = {"tender": {"additionalProcurementCategories": []}}

    additional_natures = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='contract-nature']/cbc:ProcurementTypeCode/text()",
        namespaces=namespaces,
    )

    if additional_natures:
        result["tender"]["additionalProcurementCategories"] = list(
            set(additional_natures),
        )  # Remove duplicates

    return result if result["tender"]["additionalProcurementCategories"] else None


def merge_part_additional_nature(
    release_json: dict[str, Any], part_additional_nature_data: dict[str, Any] | None
) -> None:
    """Merge part additional nature data into the main release JSON.

    Args:
        release_json: The main release JSON to merge data into
        part_additional_nature_data: The part additional nature data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not part_additional_nature_data:
        logger.warning("No part Additional Nature data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_categories = set(tender.get("additionalProcurementCategories", []))
    new_categories = set(
        part_additional_nature_data["tender"]["additionalProcurementCategories"],
    )

    combined_categories = list(existing_categories.union(new_categories))
    tender["additionalProcurementCategories"] = combined_categories

    logger.info(
        "Merged part Additional Nature data: %s categories",
        len(combined_categories),
    )
