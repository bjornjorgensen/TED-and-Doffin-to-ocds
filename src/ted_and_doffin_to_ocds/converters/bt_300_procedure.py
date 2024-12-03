# converters/bt_300_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_additional_info(
    xml_content: str | bytes,
) -> list[dict] | None:
    """
    Parse additional information from procedure-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing procedure information

    Returns:
        Optional[List[Dict]]: List of notes with text and language, or None if no data found
        The structure follows the format:
        [
            {
                "text": str,
                "language": str
            }
        ]
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

    notes = root.xpath(
        "/*/cac:ProcurementProject/cbc:Note",
        namespaces=namespaces,
    )

    result = [
        {"text": note.text, "language": note.get("languageID", "en")} for note in notes
    ]

    return result if result else None


def merge_procedure_additional_info(
    release_json: dict, procedure_additional_info: list[dict] | None
) -> None:
    """
    Merge additional information into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        procedure_additional_info (Optional[List[Dict]]): The source data containing notes
            to be merged. If None, function returns without making changes.
    """
    if not procedure_additional_info:
        return

    description = release_json.get("description", "")

    for note in procedure_additional_info:
        if description:
            description += " "
        description += note["text"]

    release_json["description"] = description
