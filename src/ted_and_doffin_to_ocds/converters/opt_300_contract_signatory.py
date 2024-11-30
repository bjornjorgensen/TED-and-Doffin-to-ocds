# converters/opt_300_contract_signatory.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_signatory_identifier_reference(xml_content):
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

    result = {"parties": [], "awards": []}

    signatory_parties = root.xpath(
        "//efac:NoticeResult/efac:SettledContract/cac:SignatoryParty/cac:PartyIdentification/cbc:ID",
        namespaces=namespaces,
    )

    for signatory in signatory_parties:
        org_id = signatory.text
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

            result["parties"].append(
                {"id": org_id, "name": org_name, "roles": ["buyer"]}
            )

        # Find the corresponding SettledContract
        contract = signatory.xpath(
            "ancestor::efac:SettledContract", namespaces=namespaces
        )[0]
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces
        )
        if contract_id:
            contract_id = contract_id[0]
            result["awards"].append({"id": contract_id, "buyers": [{"id": org_id}]})

    return result if (result["parties"] or result["awards"]) else None


def merge_signatory_identifier_reference(release_json, signatory_data) -> None:
    if not signatory_data:
        logger.info("No Signatory Identifier Reference data to merge")
        return

    parties = release_json.setdefault("parties", [])
    awards = release_json.setdefault("awards", [])

    for new_party in signatory_data.get("parties", []):
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_party["roles"] = list(
                set(existing_party.get("roles", []) + new_party["roles"])
            )
            if "name" not in existing_party and "name" in new_party:
                existing_party["name"] = new_party["name"]
        else:
            parties.append(new_party)

    for new_award in signatory_data.get("awards", []):
        existing_award = next(
            (award for award in awards if award.get("id") == new_award["id"]), None
        )
        if existing_award:
            existing_buyers = existing_award.setdefault("buyers", [])
            for new_buyer in new_award["buyers"]:
                if not any(buyer["id"] == new_buyer["id"] for buyer in existing_buyers):
                    existing_buyers.append(new_buyer)
        else:
            awards.append(new_award)

    logger.info(
        "Merged Signatory Identifier Reference data for %d parties and %d awards",
        len(signatory_data.get("parties", [])),
        len(signatory_data.get("awards", [])),
    )
