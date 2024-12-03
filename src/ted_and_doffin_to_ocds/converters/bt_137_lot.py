import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_purpose_lot_identifier(xml_content: str | bytes) -> dict | None:
    """
    Parse the lot identifiers from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot information

    Returns:
        Optional[Dict]: Dictionary containing tender lot information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lots": [
                    {
                        "id": str
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

    lot_ids = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cbc:ID/text()",
        namespaces=namespaces,
    )

    if lot_ids:
        return {"tender": {"lots": [{"id": lot_id} for lot_id in lot_ids]}}

    return None


def merge_purpose_lot_identifier(
    release_json: dict, purpose_lot_identifier_data: dict | None
) -> None:
    """
    Merge lot identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        purpose_lot_identifier_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding new lots to tender.lots
        only if they don't already exist.
    """
    if not purpose_lot_identifier_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    existing_lot_ids = {lot["id"] for lot in existing_lots}

    # Only add lots that don't already exist
    new_lots = [
        lot
        for lot in purpose_lot_identifier_data["tender"]["lots"]
        if lot["id"] not in existing_lot_ids
    ]
    existing_lots.extend(new_lots)
