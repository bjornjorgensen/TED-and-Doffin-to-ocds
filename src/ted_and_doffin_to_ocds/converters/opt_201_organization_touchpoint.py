# converters/OPT_201_organization_touchpoint.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_touchpoint_technical_identifier(xml_content):
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

    # Check if the relevant XPath exists
    relevant_xpath = "//efac:organization/efac:touchpoint/cac:partyIdentification/cbc:ID[@schemeName='touchpoint']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No touchpoint technical identifier data found. Skipping parse_touchpoint_technical_identifier."
        )
        return None

    touchpoints = root.xpath(relevant_xpath, namespaces=namespaces)

    result = {"touchpoints": []}
    for touchpoint in touchpoints:
        result["touchpoints"].append(touchpoint.text)

    return result if result["touchpoints"] else None


def merge_touchpoint_technical_identifier(release_json, touchpoint_data):
    if not touchpoint_data:
        logger.info("No touchpoint Technical Identifier data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for touchpoint_id in touchpoint_data["touchpoints"]:
        if not any(party["id"] == touchpoint_id for party in parties):
            parties.append({"id": touchpoint_id})
            logger.info(
                "Added new party with touchpoint Technical Identifier: %s",
                touchpoint_id,
            )
        else:
            logger.debug(
                "Party with touchpoint Technical Identifier %s already exists",
                touchpoint_id,
            )

    logger.info(
        "Merged %d touchpoint Technical Identifiers",
        len(touchpoint_data["touchpoints"]),
    )
