# converters/bt_134_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_public_opening_description(xml_content):
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

    lots = []

    procurement_project_lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in procurement_project_lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot.xpath(
            "cac:TenderingProcess/cac:OpenTenderEvent/cbc:Description/text()",
            namespaces=namespaces,
        )

        if description:
            lots.append({"id": lot_id, "bidOpening": {"description": description[0]}})

    logger.debug("Parsed lot public opening description data: %s", lots)
    return {"tender": {"lots": lots}} if lots else None


def merge_lot_public_opening_description(
    release_json,
    lot_public_opening_description_data,
) -> None:
    if not lot_public_opening_description_data:
        logger.warning("No Lot Public Opening Description data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_public_opening_description_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("bidOpening", {}).update(new_lot["bidOpening"])
        else:
            existing_lots.append(new_lot)

    logger.debug(
        "Release JSON after merging lot public opening description data: %s",
        release_json,
    )
    logger.info(
        "Merged Lot Public Opening Description data for %d lots",
        len(lot_public_opening_description_data["tender"]["lots"]),
    )
