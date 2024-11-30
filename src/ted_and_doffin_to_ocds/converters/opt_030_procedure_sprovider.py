# converters/opt_030_procedure_sprovider.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_provided_service_type(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Check if the relevant XPath exists
    relevant_xpath = (
        "//cac:ContractingParty/cac:Party/cac:ServiceProviderParty/cbc:ServiceTypeCode"
    )
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No provided service type data found. Skipping parse_provided_service_type."
        )
        return None

    result = {"parties": []}

    service_providers = root.xpath(
        "//cac:ContractingParty/cac:Party/cac:ServiceProviderParty",
        namespaces=namespaces,
    )
    for provider in service_providers:
        service_type = provider.xpath(
            "cbc:ServiceTypeCode/text()", namespaces=namespaces
        )
        org_id = provider.xpath(
            "cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces
        )

        if service_type and org_id:
            role = (
                "eSender"
                if service_type[0] == "ted-esen"
                else "procurementServiceProvider"
                if service_type[0] == "serv-prov"
                else None
            )
            if role:
                result["parties"].append({"id": org_id[0], "roles": [role]})

    return result if result["parties"] else None


def merge_provided_service_type(release_json, provided_service_type_data) -> None:
    if not provided_service_type_data:
        logger.info("No provided service type data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in provided_service_type_data["parties"]:
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
        "Merged provided service type data for %d parties",
        len(provided_service_type_data["parties"]),
    )
