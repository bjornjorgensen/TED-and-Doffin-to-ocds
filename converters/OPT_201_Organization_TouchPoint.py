# converters/OPT_201_Organization_TouchPoint.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_touchpoint_technical_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": []}

    touchpoints = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']", namespaces=namespaces)
    
    for touchpoint_id in touchpoints:
        result["parties"].append({
            "id": touchpoint_id.text
        })

    return result if result["parties"] else None

def merge_touchpoint_technical_identifier(release_json, touchpoint_data):
    if not touchpoint_data:
        logger.warning("No TouchPoint Technical Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in touchpoint_data["parties"]:
        if not any(party["id"] == new_party["id"] for party in existing_parties):
            existing_parties.append(new_party)

    logger.info(f"Merged TouchPoint Technical Identifier data for {len(touchpoint_data['parties'])} touchpoints")