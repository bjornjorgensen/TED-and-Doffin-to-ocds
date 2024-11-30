# converters/opt_201_organization_touchpoint.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_technical_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"parties": []}

    touchpoints = root.xpath(
        "//efac:Organizations/efac:Organization/efac:TouchPoint/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']",
        namespaces=namespaces,
    )

    for touchpoint in touchpoints:
        touchpoint_id = touchpoint.text
        if touchpoint_id:
            result["parties"].append({"id": touchpoint_id})

    return result if result["parties"] else None


def merge_touchpoint_technical_identifier(release_json, touchpoint_data) -> None:
    if not touchpoint_data:
        logger.info("No TouchPoint technical identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_data["parties"]:
        if not any(
            existing_party["id"] == new_party["id"]
            for existing_party in existing_parties
        ):
            existing_parties.append(new_party)
            logger.info("Added new party with TouchPoint id: %s", new_party["id"])
        else:
            logger.info(
                "Party with TouchPoint id: %s already exists, skipping", new_party["id"]
            )

    logger.info(
        "Merged TouchPoint technical identifier data for %d parties",
        len(touchpoint_data["parties"]),
    )
