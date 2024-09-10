# converters/BT_5071_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_country_subdivision(xml_content):
    """
    Parse the XML content to extract the place performance country subdivision (NUTS3 code) for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed place performance country subdivision data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        nuts_codes = lot.xpath(
            ".//cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode[@listName='nuts=lvl3']/text()",
            namespaces=namespaces,
        )

        if nuts_codes:
            item_data = {
                "id": str(len(result["tender"]["items"]) + 1),
                "deliveryAddresses": [
                    {"region": nuts_code} for nuts_code in nuts_codes
                ],
                "relatedLot": lot_id,
            }
            result["tender"]["items"].append(item_data)

    return result if result["tender"]["items"] else None


def merge_place_performance_country_subdivision(release_json, subdivision_data):
    """
    Merge the parsed place performance country subdivision data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        subdivision_data (dict): The parsed place performance country subdivision data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not subdivision_data:
        logger.warning("No place performance country subdivision data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in subdivision_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            for new_address in new_item["deliveryAddresses"]:
                existing_address = next(
                    (addr for addr in existing_addresses if "region" not in addr), None
                )
                if existing_address:
                    existing_address["region"] = new_address["region"]
                else:
                    existing_addresses.append(new_address)
        else:
            existing_items.append(new_item)

    logger.info(
        f"Merged place performance country subdivision data for {len(subdivision_data['tender']['items'])} items"
    )
