import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_acquiring_cpb_buyer_indicator(xml_content: str | bytes) -> dict | None:
    """Parse XML content to find organizations marked as wholesale buyers.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Dict containing parties with wholesale buyer roles, or None if no wholesale buyers found
        Example:
        {
            "parties": [
                {
                    "id": "ORG-0001",
                    "roles": ["wholesaleBuyer"]
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

    wholesale_orgs = root.xpath(
        """//efac:Organizations/efac:Organization[
            efbc:AcquiringCPBIndicator and
            efbc:AcquiringCPBIndicator[translate(text(), 'TRUE', 'true')='true']
        ]/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()""",
        namespaces=namespaces,
    )

    if not wholesale_orgs:
        logger.debug("No wholesale buyers found in the XML")
        return None

    logger.debug("Found %d wholesale buyer(s)", len(wholesale_orgs))
    return {
        "parties": [
            {"id": org_id, "roles": ["wholesaleBuyer"]} for org_id in wholesale_orgs
        ]
    }


def merge_acquiring_cpb_buyer_indicator(
    release_json: dict, wholesale_buyer_data: dict | None
) -> None:
    """Merge wholesale buyer data into the release while preserving other parties and roles.

    Args:
        release_json: The release to merge into
        wholesale_buyer_data: Data about wholesale buyers to merge, or None if no data
    """
    if not wholesale_buyer_data:
        logger.debug("No Acquiring CPB Buyer Indicator data to merge")
        return

    # Initialize parties list if not present
    parties = release_json.setdefault("parties", [])

    # Remove any existing wholesaleBuyer roles
    for party in parties:
        if "roles" in party:
            party["roles"] = [
                role for role in party["roles"] if role != "wholesaleBuyer"
            ]

    # Add new wholesale buyers
    for new_party in wholesale_buyer_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_party.setdefault("roles", []).append("wholesaleBuyer")
        else:
            parties.append(new_party)

    logger.debug(
        "Merged Acquiring CPB Buyer Indicator data for %(num_parties)s parties",
        {"num_parties": len(wholesale_buyer_data["parties"])},
    )
