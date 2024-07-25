# converters/BT_300_Part.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_part_additional_info(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    part_notes = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Note", namespaces=namespaces)
    
    for note in part_notes:
        note_text = note.text
        language = note.get('languageID', 'en')  # Default to 'en' if languageID is not present
        result.append({'text': note_text, 'language': language})

    return result if result else None

def merge_part_additional_info(release_json, part_additional_info):
    if not part_additional_info:
        logger.info("No part additional information to merge")
        return

    description = release_json.get('description', '')

    for note in part_additional_info:
        if description:
            description += ' '
        description += note['text']

    release_json['description'] = description

    logger.info(f"Merged additional information for the release description")