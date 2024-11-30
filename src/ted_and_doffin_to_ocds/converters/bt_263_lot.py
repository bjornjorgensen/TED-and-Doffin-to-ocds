# converters/bt_263_lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_classification_code(xml_content):
    """
    Parse the XML content to extract the additional classification code for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed additional classification code data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No additional classification code data found. Skipping parse_additional_classification_code."
        )
        return None

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        classification_codes = lot.xpath(
            "cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode/text()",
            namespaces=namespaces,
        )

        if classification_codes:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "additionalClassifications": [
                    {"id": code} for code in classification_codes
                ],
                "relatedLot": lot_id,
            }
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_additional_classification_code(
    release_json, additional_classification_data
) -> None:
    """
    Merge the parsed additional classification code data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        additional_classification_data (dict): The parsed additional classification code data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not additional_classification_data:
        logger.info("No additional classification code data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in additional_classification_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            existing_classifications = existing_item.setdefault(
                "additionalClassifications", []
            )
            for new_classification in new_item["additionalClassifications"]:
                if new_classification not in existing_classifications:
                    existing_classifications.append(new_classification)
        else:
            existing_items.append(new_item)

    logger.info(
        "Merged additional classification code data for %d items",
        len(additional_classification_data["tender"]["items"]),
    )
