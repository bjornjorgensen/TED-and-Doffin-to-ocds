# converters/BT_300_Part.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_part_additional_info(xml_content):
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

    result = []

    part_notes = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Note",
        namespaces=namespaces,
    )

    for note in part_notes:
        note_text = note.text
        language = note.get(
            "languageID", "en"
        )  # Default to 'en' if languageID is not present
        result.append({"text": note_text, "language": language})

    return result if result else None


def merge_part_additional_info(release_json, part_additional_info):
    if not part_additional_info:
        logger.info("No part additional information to merge")
        return

    description = release_json.get("description", "")

    for note in part_additional_info:
        if description:
            description += " "
        description += note["text"]

    release_json["description"] = description

    logger.info(f"Merged additional information for the release description")
