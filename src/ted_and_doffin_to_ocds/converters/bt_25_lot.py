# converters/bt_25_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_quantity(xml_content):
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

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for i, lot in enumerate(lots, start=1):
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        quantity = lot.xpath(
            "cac:ProcurementProject/cbc:EstimatedOverallContractQuantity/text()",
            namespaces=namespaces,
        )
        unit_code = lot.xpath(
            "cac:ProcurementProject/cbc:EstimatedOverallContractQuantity/@unitCode",
            namespaces=namespaces,
        )

        if quantity:
            item = {"id": str(i), "quantity": float(quantity[0]), "relatedLot": lot_id}
            if unit_code:
                item["unit"] = {"id": unit_code[0]}
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_lot_quantity(release_json, lot_quantity_data):
    if not lot_quantity_data:
        logger.warning("No Lot Quantity data to merge")
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in lot_quantity_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            existing_item.update(new_item)
        else:
            existing_items.append(new_item)

    logger.info(
        "Merged Lot Quantity data for %(num_items)d items",
        {"num_items": len(lot_quantity_data["tender"]["items"])},
    )
