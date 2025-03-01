# converters/bt_766_partDynamicPurchasingSystem.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_dynamic_purchasing_system(xml_content: str) -> dict | None:
    """Parse the XML content to extract the Dynamic Purchasing System details for the part.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data if found, None otherwise.

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

    type_mapping = {"dps-list": "closed", "dps-nlist": "open"}

    dps_usage = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='dps-usage']/cbc:ContractingSystemTypeCode/text()",
        namespaces=namespaces,
    )

    if not dps_usage or dps_usage[0] == "none":
        return None

    mapped_type = type_mapping.get(dps_usage[0])
    if mapped_type:
        return {
            "tender": {
                "techniques": {
                    "hasDynamicPurchasingSystem": True,
                    "dynamicPurchasingSystem": {"type": mapped_type},
                },
            },
        }

    return None


def merge_part_dynamic_purchasing_system(
    release_json: dict,
    part_dynamic_purchasing_system_data: dict | None,
) -> None:
    """Merge the parsed part Dynamic Purchasing System data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        part_dynamic_purchasing_system_data (Optional[Dict]): The parsed part Dynamic Purchasing System data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not part_dynamic_purchasing_system_data:
        logger.warning("No part Dynamic Purchasing System data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}

    if part_dynamic_purchasing_system_data["tender"].get("techniques"):
        if "techniques" not in release_json["tender"]:
            release_json["tender"]["techniques"] = {}
        release_json["tender"]["techniques"].update(
            part_dynamic_purchasing_system_data["tender"]["techniques"]
        )

    logger.info("Merged part Dynamic Purchasing System data")
