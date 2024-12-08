import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_public_opening_description(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the public opening description from lot-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot information

    Returns:
        Optional[Dict]: Dictionary containing tender lot information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "bidOpening": {
                            "description": str
                        }
                    }
                ]
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        description = lot.xpath(
            "cac:TenderingProcess/cac:OpenTenderEvent/cbc:Description/text()",
            namespaces=namespaces,
        )

        if description:
            lot_data = {
                "id": lot_id,
                "bidOpening": {"description": description[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_public_opening_description(
    release_json: dict, lot_public_opening_description_data: dict | None
) -> None:
    """Merge public opening description data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        lot_public_opening_description_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.lots.bidOpening.description field for matching lots.

    """
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

    logger.info(
        "Merged Lot Public Opening Description data for %d lots",
        len(lot_public_opening_description_data["tender"]["lots"]),
    )
