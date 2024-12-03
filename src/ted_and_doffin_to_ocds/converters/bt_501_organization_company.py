# converters/bt_501_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_identifier(xml_content: str | bytes) -> dict | None:
    """
    Parse organization identifier information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization information

    Returns:
        Optional[Dict]: A dictionary containing parsed organization data in OCDS format with
        'parties' array, or None if no valid organization data is found.
        Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "additionalIdentifiers": [{
                    "id": "09506232",
                    "scheme": "GB-COH"
                }]
            }]
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
    }

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization", namespaces=namespaces
    )
    for org in organizations:
        org_id = org.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        company_id = org.xpath(
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


def merge_organization_identifier(
    release_json: dict, organization_identifier_data: dict | None
) -> None:
    """
    Merge organization identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        organization_identifier_data (Optional[Dict]): Organization identifier data to merge,
            containing a 'parties' array with organization information

    Returns:
        None: Modifies release_json in place

    Note:
        If organization_identifier_data is None or contains no parties, no changes are made.
        For existing parties, new identifiers are appended to additionalIdentifiers if not present.
    """
    if not organization_identifier_data:
        logger.info("No organization identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_identifier_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_identifiers = existing_party.setdefault(
                "additionalIdentifiers", []
            )
            for new_identifier in new_party["additionalIdentifiers"]:
                if new_identifier not in existing_identifiers:
                    existing_identifiers.append(new_identifier)
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization identifier data for %d parties",
        len(organization_identifier_data["parties"]),
    )
