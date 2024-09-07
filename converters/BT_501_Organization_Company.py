# converters/BT_501_Organization_Company.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_identifier(xml_content):
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

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization", namespaces=namespaces
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        company_id = organization.xpath(
            "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
            namespaces=namespaces,
        )

        if org_id and company_id:
            party = {
                "id": org_id[0],
                "additionalIdentifiers": [
                    {
                        "id": company_id[0],
                        "scheme": "GB-COH",  # Assuming GB-COH scheme for this example
                    }
                ],
            }
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_identifier(release_json, organization_identifier_data):
    if not organization_identifier_data:
        logger.warning("No Organization Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_identifier_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("additionalIdentifiers", []).extend(
                new_party["additionalIdentifiers"]
            )
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged Organization Identifier data for {len(organization_identifier_data['parties'])} parties"
    )
