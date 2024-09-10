# converters/BT_512_UBO.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_postcode(xml_content):
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

    organizations = root.xpath("//efac:Organizations", namespaces=namespaces)

    for org in organizations:
        company_id = org.xpath(
            "efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        ubo_id = org.xpath(
            "efac:UltimateBeneficialOwner/cbc:ID[@schemeName='ubo']/text()",
            namespaces=namespaces,
        )
        postal_zone = org.xpath(
            "efac:UltimateBeneficialOwner/cac:ResidenceAddress/cbc:PostalZone/text()",
            namespaces=namespaces,
        )

        if company_id and ubo_id and postal_zone:
            party = {
                "id": company_id[0],
                "beneficialOwners": [
                    {"id": ubo_id[0], "address": {"postalCode": postal_zone[0]}}
                ],
            }
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_ubo_postcode(release_json, ubo_postcode_data):
    if not ubo_postcode_data:
        logger.warning("No UBO Postcode data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_postcode_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners", []
            )
            for new_ubo in new_party["beneficialOwners"]:
                existing_ubo = next(
                    (
                        ubo
                        for ubo in existing_beneficial_owners
                        if ubo["id"] == new_ubo["id"]
                    ),
                    None,
                )
                if existing_ubo:
                    existing_ubo.setdefault("address", {}).update(new_ubo["address"])
                else:
                    existing_beneficial_owners.append(new_ubo)
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged UBO Postcode data for {len(ubo_postcode_data['parties'])} parties"
    )
