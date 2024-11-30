# converters/bt_263_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_classification_code_procedure(xml_content):
    """
    Parse the XML content to extract the additional classification code for the procedure.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed additional classification code data for the procedure.
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
    relevant_xpath = "/*/cac:ProcurementProject/cac:AdditionalCommodityClassification/cbc:ItemClassificationCode"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No additional classification code data found for procedure. Skipping parse_additional_classification_code_procedure."
        )
        return None

    result = {"tender": {"items": []}}

    classification_codes = root.xpath(relevant_xpath, namespaces=namespaces)

    if classification_codes:
        item = {
            "id": "1",
            "additionalClassifications": [
                {"id": code.text} for code in classification_codes
            ],
        }
        result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_additional_classification_code_procedure(
    release_json, additional_classification_data
) -> None:
    """
    Merge the parsed additional classification code data for procedure into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        additional_classification_data (dict): The parsed additional classification code data for procedure to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not additional_classification_data:
        logger.info("No additional classification code data for procedure to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in additional_classification_data["tender"]["items"]:
        existing_item = next(
            (item for item in existing_items if item["id"] == new_item["id"]),
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
        "Merged additional classification code data for procedure with %d classifications",
        len(
            additional_classification_data["tender"]["items"][0][
                "additionalClassifications"
            ]
        ),
    )
