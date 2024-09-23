# converters/BT_300_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_lot_additional_info(xml_content):
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

    lot_notes = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:ProcurementProject/cbc:Note",
        namespaces=namespaces,
    )

    for note in lot_notes:
        lot_id = note.xpath(
            "../../cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )[0]
        note_text = note.text
        language = note.get(
            "languageID",
            "en",
        )  # Default to 'en' if languageID is not present

        if lot_id not in result:
            result[lot_id] = []

        result[lot_id].append({"text": note_text, "language": language})

    return result if result else None


def merge_lot_additional_info(release_json, lot_additional_info):
    if not lot_additional_info:
        logger.info("No lot additional information to merge")
        return

    lots = release_json.get("tender", {}).get("lots", [])

    for lot in lots:
        lot_id = lot.get("id")
        if lot_id in lot_additional_info:
            notes = lot_additional_info[lot_id]
            description = lot.get("description", "")
            for note in notes:
                if description:
                    description += " "
                description += note["text"]
            lot["description"] = description

    logger.info(f"Merged additional information for {len(lot_additional_info)} lots")
