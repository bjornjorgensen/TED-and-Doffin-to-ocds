# converters/OPP_040_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_main_nature_sub_type(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse main nature sub type information (OPP-040) from XML content.

    Gets transport service type codes and adds them to the tender's
    additionalProcurementCategories array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing procurement categories or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"additionalProcurementCategories": []}}

        type_codes = root.xpath(
            "//cac:ProcurementProject/cac:ProcurementAdditionalType"
            "[cbc:ProcurementTypeCode/@listName='transport-service']"
            "/cbc:ProcurementTypeCode/text()",
            namespaces=NAMESPACES,
        )

        if type_codes:
            # Filter out any empty strings and add valid codes
            valid_codes = [code.strip() for code in type_codes if code.strip()]
            if valid_codes:
                result["tender"]["additionalProcurementCategories"] = valid_codes
                return result

    except Exception:
        logger.exception("Error parsing main nature sub type")
        return None

    return None


def merge_main_nature_sub_type(
    release_json: dict[str, Any], nature_type_data: dict[str, Any] | None
) -> None:
    """
    Merge main nature sub type information into the release JSON.

    Updates or creates additionalProcurementCategories array with transport service codes.
    Preserves existing categories while adding new ones.

    Args:
        release_json: The target release JSON to update
        nature_type_data: The source data containing procurement categories to merge

    Returns:
        None
    """
    if not nature_type_data:
        logger.warning("No main nature sub type data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_categories = tender.setdefault("additionalProcurementCategories", [])

    new_categories = nature_type_data["tender"]["additionalProcurementCategories"]
    for category in new_categories:
        if category not in existing_categories:
            existing_categories.append(category)

    logger.info(
        "Merged main nature sub type: added %d categories",
        len(new_categories),
    )
