# converters/opp_050_organization.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyers_group_lead_indicator(xml_content):
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

    # Only select organizations that explicitly have GroupLeadIndicator as true or 1
    lead_orgs = root.xpath(
        """//efac:Organizations/efac:Organization[
            efbc:GroupLeadIndicator and
            (efbc:GroupLeadIndicator[translate(text(), 'TRUE', 'true')='true'] or
             efbc:GroupLeadIndicator[text()='1'])
        ]/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()""",
        namespaces=namespaces,
    )

    if not lead_orgs:
        logger.debug("No lead buyers found in the XML")
        return None

    logger.debug("Found %d lead buyer(s)", len(lead_orgs))
    return {"parties": [{"id": org_id, "roles": ["leadBuyer"]} for org_id in lead_orgs]}


def merge_buyers_group_lead_indicator(release_json, lead_buyer_data) -> None:
    """Merge lead buyer data into the release while preserving other parties and roles"""
    if not lead_buyer_data:
        logger.debug("No Buyers Group Lead Indicator data to merge")
        return

    # Initialize parties list if not present
    parties = release_json.setdefault("parties", [])

    # Remove any existing leadBuyer roles
    for party in parties:
        if "roles" in party:
            party["roles"] = [role for role in party["roles"] if role != "leadBuyer"]

    # Add new lead buyers
    for new_party in lead_buyer_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_party.setdefault("roles", []).append("leadBuyer")
        else:
            parties.append(new_party)

    logger.debug(
        "Merged Buyers Group Lead Indicator data for %(num_parties)s parties",
        {"num_parties": len(lead_buyer_data["parties"])},
    )
