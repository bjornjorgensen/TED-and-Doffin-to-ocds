# converters/OPT_160_ubo.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_ubo_first_name(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

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

    for org in organizations:
        org_id = org.xpath(
            ".//cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        if not org_id:
            continue
        org_id = org_id[0]

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
            first_name = ubo.xpath("cbc:FirstName/text()", namespaces=namespaces)

            if ubo_id and first_name:
                beneficial_owners.append({"id": ubo_id[0], "name": first_name[0]})

        if beneficial_owners:
            result["parties"].append(
                {"id": org_id, "beneficialOwners": beneficial_owners},
            )

    return result if result["parties"] else None


def merge_ubo_first_name(release_json, ubo_data):
    if not ubo_data:
        logger.warning("No ubo First Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_data["parties"]:
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
                    existing_bo["name"] = new_bo["name"]
                else:
                    existing_beneficial_owners.append(new_bo)
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged ubo First Name data for {len(ubo_data['parties'])} parties")
