# converters/bt_300_LotsGroup.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_lotsgroup_additional_info(xml_content):
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

    lotsgroup_notes = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:ProcurementProject/cbc:Note",
        namespaces=namespaces,
    )

    for note in lotsgroup_notes:
        lotsgroup_id = note.xpath(
            "../../cbc:ID[@schemeName='LotsGroup']/text()",
            namespaces=namespaces,
        )[0]
        note_text = note.text
        language = note.get(
            "languageID",
            "en",
        )  # Default to 'en' if languageID is not present

        if lotsgroup_id not in result:
            result[lotsgroup_id] = []

        result[lotsgroup_id].append({"text": note_text, "language": language})

    return result if result else None


def merge_lotsgroup_additional_info(release_json, lotsgroup_additional_info):
    if not lotsgroup_additional_info:
        logger.info("No lots group additional information to merge")
        return

    lot_groups = release_json.get("tender", {}).get("lotGroups", [])
    merged_count = 0

    for lot_group in lot_groups:
        lot_group_id = lot_group.get("id")
        if lot_group_id in lotsgroup_additional_info:
            notes = lotsgroup_additional_info[lot_group_id]
            description = lot_group.get("description", "")

            for note in notes:
                if description:
                    description += " "
                description += note["text"]

            lot_group["description"] = description
            merged_count += 1

    logger.info("Merged additional information for %d lots groups", merged_count)
