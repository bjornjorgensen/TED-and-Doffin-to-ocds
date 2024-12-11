# converters/bt_766_DynamicPurchasingSystem.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_dynamic_purchasing_system(xml_content: str) -> dict[str, dict] | None:
    """Parse the XML content to extract the Dynamic Purchasing System details for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict[str, Dict]]: A dictionary mapping lot IDs to their DPS data if found, None otherwise.

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

    lots_data = {}
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        dps_usage = lot.xpath(
            "cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='dps-usage']/cbc:ContractingSystemTypeCode/text()",
            namespaces=namespaces,
        )

        if dps_usage and dps_usage[0] != "none":
            mapped_type = type_mapping.get(dps_usage[0])
            if mapped_type:
                lots_data[lot_id] = {
                    "techniques": {
                        "hasDynamicPurchasingSystem": True,
                        "dynamicPurchasingSystem": {"type": mapped_type},
                    },
                }

    return lots_data if lots_data else None


def merge_dynamic_purchasing_system(
    release_json: dict,
    dynamic_purchasing_system_data: dict[str, dict] | None,
) -> None:
    """Merge the parsed Dynamic Purchasing System data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        dynamic_purchasing_system_data (Optional[Dict[str, Dict]]): The parsed Dynamic Purchasing System data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not dynamic_purchasing_system_data:
        logger.warning("No Dynamic Purchasing System data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    updated_lots = []
    for lot in lots:
        lot_id = lot["id"]
        if lot_id in dynamic_purchasing_system_data:
            lot.update(dynamic_purchasing_system_data[lot_id])
            updated_lots.append(lot)

    tender["lots"] = updated_lots

    logger.info("Merged Dynamic Purchasing System data for %d lots", len(updated_lots))
