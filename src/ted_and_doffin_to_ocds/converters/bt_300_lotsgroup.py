import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lotsgroup_additional_info(xml_content: str | bytes) -> dict | None:
    """
    Parse additional information from lot group-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot group information

    Returns:
        Optional[Dict]: Dictionary containing lot group information keyed by group ID, or None if no data found
        The structure follows the format:
        {
            "GLO-0001": [
                {
                    "text": str,
                    "language": str
                }
            ]
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

    result = {}

    group_notes = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:ProcurementProject/cbc:Note",
        namespaces=namespaces,
    )

    for note in group_notes:
        group_id = note.xpath(
            "../../cbc:ID[@schemeName='LotsGroup']/text()",
            namespaces=namespaces,
        )[0]
        note_text = note.text
        language = note.get("languageID", "en")

        if group_id not in result:
            result[group_id] = []

        result[group_id].append({"text": note_text, "language": language})

    return result if result else None


def merge_lotsgroup_additional_info(
    release_json: dict, lotsgroup_additional_info: dict | None
) -> None:
    """
    Merge additional information into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        lotsgroup_additional_info (Optional[Dict]): The source data containing lot group information
            to be merged. If None, function returns without making changes.
    """
    if not lotsgroup_additional_info:
        return

    lot_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])

    for lot_group in lot_groups:
        group_id = lot_group.get("id")
        if group_id in lotsgroup_additional_info:
            notes = lotsgroup_additional_info[group_id]
            description = lot_group.get("description", "")
            for note in notes:
                if description:
                    description += " "
                description += note["text"]
            lot_group["description"] = description
