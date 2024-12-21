import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_awarding_cpb_buyer_indicator(xml_content: str | bytes) -> dict | None:
    """Parse XML content to find organizations marked as procuring entities.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Dict containing parties with procuring entity roles, or None if no procuring entities found
        Example:
        {
            "parties": [
                {
                    "id": "ORG-0001",
                    "roles": ["procuringEntity"]
                }
            ]
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    # Only select organizations that explicitly have AwardingCPBIndicator as true
    procuring_orgs = root.xpath(
        """//efac:Organizations/efac:Organization[
            efbc:AwardingCPBIndicator and
            efbc:AwardingCPBIndicator[translate(text(), 'TRUE', 'true')='true']
        ]/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()""",
        namespaces=namespaces,
    )

    if not procuring_orgs:
        logger.debug("No procuring entities found in the XML")
        return None

    logger.debug("Found %d procuring entity(ies)", len(procuring_orgs))
    return {
        "parties": [
            {"id": org_id, "roles": ["procuringEntity"]} for org_id in procuring_orgs
        ]
    }


def merge_awarding_cpb_buyer_indicator(
    release_json: dict, procuring_entity_data: dict | None
) -> None:
    """Merge procuring entity data into the release while preserving other parties and roles.

    Args:
        release_json: The release to merge into
        procuring_entity_data: Data about procuring entities to merge, or None if no data

    """
    if not procuring_entity_data:
        logger.debug("No Awarding CPB Buyer Indicator data to merge")
        return

    # Initialize parties list if not present
    parties = release_json.setdefault("parties", [])

    # Remove any existing procuringEntity roles
    for party in parties:
        if "roles" in party:
            party["roles"] = [
                role for role in party["roles"] if role != "procuringEntity"
            ]

    # Add new procuring entities
    for new_party in procuring_entity_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_party.setdefault("roles", []).append("procuringEntity")
        else:
            parties.append(new_party)

    logger.debug(
        "Merged Awarding CPB Buyer Indicator data for %(num_parties)s parties",
        {"num_parties": len(procuring_entity_data["parties"])},
    )
