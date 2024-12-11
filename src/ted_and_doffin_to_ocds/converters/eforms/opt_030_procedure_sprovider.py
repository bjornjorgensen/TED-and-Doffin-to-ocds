# converters/opt_030_procedure_sprovider.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

ROLE_MAPPING = {
    "ted-esen": "eSender",
    "serv-prov": "procurementServiceProvider",
}


def parse_provided_service_type(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse provided service type information (OPT-030) from XML content.

    Gets service provider organizations and maps their roles based on service type.
    Creates/updates corresponding Organization objects in parties array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing parties with roles or None if no data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"parties": []}

        providers = root.xpath(
            "/*/cac:ContractingParty/cac:Party/cac:ServiceProviderParty",
            namespaces=NAMESPACES,
        )

        for provider in providers:
            try:
                org_id = provider.xpath(
                    "cac:Party/cac:PartyIdentification/cbc:ID/text()",
                    namespaces=NAMESPACES,
                )[0]

                service_type = provider.xpath(
                    "cbc:ServiceTypeCode[@listName='organisation-role']/text()",
                    namespaces=NAMESPACES,
                )[0]

                if org_id and service_type in ROLE_MAPPING:
                    result["parties"].append(
                        {"id": org_id, "roles": [ROLE_MAPPING[service_type]]}
                    )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete service provider data: %s", e)
                continue

        if result["parties"]:
            return result

    except Exception:
        logger.exception("Error parsing provided service type")
        return None

    return None


def merge_provided_service_type(
    release_json: dict[str, Any], service_type_data: dict[str, Any] | None
) -> None:
    """Merge provided service type information into the release JSON.

    Updates or creates parties with role information.
    Preserves existing party data while adding/updating roles.

    Args:
        release_json: The target release JSON to update
        service_type_data: The source data containing service roles to merge

    Returns:
        None

    """
    if not service_type_data:
        logger.warning("No provided service type data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in service_type_data["parties"]:
        existing_party = next(
            (p for p in parties if p["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_roles = existing_party.setdefault("roles", [])
            for role in new_party["roles"]:
                if role not in existing_roles:
                    existing_roles.append(role)
        else:
            parties.append(new_party)

    logger.info(
        "Merged provided service type data for %d parties",
        len(service_type_data["parties"]),
    )
