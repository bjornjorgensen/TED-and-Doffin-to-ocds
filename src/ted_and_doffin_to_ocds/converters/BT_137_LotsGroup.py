# converters/BT_137_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lots_group_identifier(xml_content):
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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cbc:ID"
    lots_group_ids = root.xpath(xpath, namespaces=namespaces)

    if lots_group_ids:
        return {
            "tender": {
                "lotGroups": [
                    {"id": lots_group_id.text} for lots_group_id in lots_group_ids
                ],
            },
        }
    logger.info("No lots group identifiers found")
    return None


def merge_lots_group_identifier(release_json, lots_group_data):
    if not lots_group_data:
        logger.warning("No lots group identifier data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_lot_group in lots_group_data["tender"]["lotGroups"]:
        if not any(
            lot_group["id"] == new_lot_group["id"] for lot_group in existing_lot_groups
        ):
            existing_lot_groups.append(new_lot_group)
            logger.info(f"Added new lot group with id: {new_lot_group['id']}")
        else:
            logger.info(
                f"Lot group with id: {new_lot_group['id']} already exists, skipping",
            )
