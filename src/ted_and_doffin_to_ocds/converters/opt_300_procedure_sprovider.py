# converters/opt_300_procedure_sprovider.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_service_provider_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse service provider information from XML content.

    Gets service provider details and their organization names from the Organizations section.
    Only creates party entries for service providers that have valid organization references.

    Args:
        xml_content: XML content containing service provider data

    Returns:
        Optional[Dict]: Dictionary containing parties with names, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "name": "Service Provider Name"
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
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"parties": []}

    service_providers = root.xpath(
        "//cac:ContractingParty/cac:Party/cac:ServiceProviderParty/cac:Party/cac:PartyIdentification/cbc:ID",
        namespaces=namespaces,
    )

    for provider in service_providers:
        org_id = provider.text
        if not org_id:
            continue

        # Find the corresponding organization details
        org = root.xpath(
            f"//efac:Organizations/efac:Organization/efac:Company[cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()='{org_id}']",
            namespaces=namespaces,
        )
        if org:
            org_name = org[0].xpath(
                "cac:PartyName/cbc:Name/text()", namespaces=namespaces
            )
            org_name = org_name[0] if org_name else None

            result["parties"].append({"id": org_id, "name": org_name})

    return result if result["parties"] else None


def merge_service_provider_identifier(
    release_json: dict[str, Any], provider_data: dict[str, Any] | None
) -> None:
    """Merge service provider data into the release JSON.

    Args:
        release_json: Target release JSON to update
        provider_data: Service provider data containing organization details

    Effects:
        Updates the parties section of release_json with service provider information,
        adding names to existing parties or creating new party entries

    """
    if not provider_data:
        logger.info("No Service Provider Technical Identifier Reference data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in provider_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "name" not in existing_party and "name" in new_party:
                existing_party["name"] = new_party["name"]
        else:
            parties.append(new_party)

    logger.info(
        "Merged Service Provider Technical Identifier Reference data for %s parties",
        len(provider_data["parties"]),
    )
