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

    # Using a more specific XPath to select only organizations with GroupLeadIndicator="true"
    lead_orgs = root.xpath(
        """//efac:Organizations/efac:Organization[
            efbc:GroupLeadIndicator[translate(text(), 'TRUE', 'true')='true']
        ]/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()""",
        namespaces=namespaces,
    )

    if not lead_orgs:
        return None

    return {"parties": [{"id": org_id, "roles": ["leadBuyer"]} for org_id in lead_orgs]}


def merge_buyers_group_lead_indicator(release_json, lead_buyer_data) -> None:
    if not lead_buyer_data:
        logger.info("No Buyers Group Lead Indicator data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for new_party in lead_buyer_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_party.setdefault("roles", []).extend(
                role
                for role in new_party["roles"]
                if role not in existing_party["roles"]
            )
        else:
            parties.append(new_party)

    logger.info(
        "Merged Buyers Group Lead Indicator data for %(num_parties)s parties",
        {"num_parties": len(lead_buyer_data["parties"])},
    )
