# converters/bt_507_ubo.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_country_subdivision(xml_content):
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
        "//efac:organizations/efac:organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:company/cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )

        if org_id:
            ubos = root.xpath(
                "//efac:organizations/efac:UltimateBeneficialOwner",
                namespaces=namespaces,
            )
            beneficial_owners = []

            for ubo in ubos:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()",
                    namespaces=namespaces,
                )
                country_subentity_code = ubo.xpath(
                    "cac:ResidenceAddress/cbc:CountrySubentityCode[@listName='nuts']/text()",
                    namespaces=namespaces,
                )

                if ubo_id and country_subentity_code:
                    beneficial_owner = {
                        "id": ubo_id[0],
                        "address": {"region": country_subentity_code[0]},
                    }
                    beneficial_owners.append(beneficial_owner)

            if beneficial_owners:
                party_data = {"id": org_id[0], "beneficialOwners": beneficial_owners}
                result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_ubo_country_subdivision(release_json, ubo_country_subdivision_data):
    if not ubo_country_subdivision_data:
        logger.warning("No ubo country subdivision data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_country_subdivision_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners",
                [],
            )
            for new_bo in new_party["beneficialOwners"]:
                existing_bo = next(
                    (
                        bo
                        for bo in existing_beneficial_owners
                        if bo["id"] == new_bo["id"]
                    ),
                    None,
                )
                if existing_bo:
                    existing_bo.setdefault("address", {}).update(new_bo["address"])
                else:
                    existing_beneficial_owners.append(new_bo)
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged ubo country subdivision data for %s parties",
        len(ubo_country_subdivision_data["parties"]),
    )
