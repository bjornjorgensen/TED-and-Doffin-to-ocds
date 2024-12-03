# converters/bt_137_part.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_identifier(xml_content: str | bytes) -> dict | None:
    """
    Parse the part identifier from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing part information

    Returns:
        Optional[Dict]: Dictionary containing tender information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "id": str  # Part identifier
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

    part_ids = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cbc:ID/text()",
        namespaces=namespaces,
    )

    if part_ids:
        # Take the first part ID found as tender.id should be a single value
        return {"tender": {"id": part_ids[0]}}

    return None


def merge_part_identifier(release_json: dict, part_data: dict | None) -> None:
    """
    Merge part identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        part_data (Optional[Dict]): The source data containing tender part ID
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by setting the
        tender.id field.
    """
    if not part_data:
        return

    tender = release_json.setdefault("tender", {})
    tender["id"] = part_data["tender"]["id"]
