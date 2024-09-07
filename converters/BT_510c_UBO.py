# converters/BT_510c_UBO.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_streetline2(xml_content):
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

        if org_id:
            ubos = root.xpath(
                "//efac:Organizations/efac:UltimateBeneficialOwner",
                namespaces=namespaces,
            )
            beneficial_owners = []

            for ubo in ubos:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces
                )

                if ubo_id:
                    street_name = ubo.xpath(
                        "cac:ResidenceAddress/cbc:StreetName/text()",
                        namespaces=namespaces,
                    )
                    additional_street_name = ubo.xpath(
                        "cac:ResidenceAddress/cbc:AdditionalStreetName/text()",
                        namespaces=namespaces,
                    )
                    address_lines = ubo.xpath(
                        "cac:ResidenceAddress/cac:AddressLine/cbc:Line/text()",
                        namespaces=namespaces,
                    )

                    street_address_parts = []
                    if street_name:
                        street_address_parts.append(street_name[0])
                    if additional_street_name:
                        street_address_parts.append(additional_street_name[0])
                    street_address_parts.extend(address_lines)

                    street_address = ", ".join(street_address_parts)

                    if street_address:
                        beneficial_owner = {
                            "id": ubo_id[0],
                            "address": {"streetAddress": street_address},
                        }
                        beneficial_owners.append(beneficial_owner)

            if beneficial_owners:
                party = {"id": org_id[0], "beneficialOwners": beneficial_owners}
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_ubo_streetline2(release_json, ubo_streetline2_data):
    if not ubo_streetline2_data:
        logger.warning("No UBO Streetline 2 data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_streetline2_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners", []
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
        f"Merged UBO Streetline 2 data for {len(ubo_streetline2_data['parties'])} parties"
    )
