# converters/opt_300_procedure_sprovider.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_service_provider_identifier(xml_content):
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


def merge_service_provider_identifier(release_json, provider_data):
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
