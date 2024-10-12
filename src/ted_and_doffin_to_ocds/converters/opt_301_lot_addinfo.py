# converters/opt_301_lot_addinfo.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_additional_info_provider(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": []}

    additional_info_parties = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AdditionalInformationParty/cac:PartyIdentification/cbc:ID",
        namespaces=namespaces,
    )

    for party in additional_info_parties:
        org_id = party.text
        if org_id:
            result["parties"].append({"id": org_id, "roles": ["processContactPoint"]})

    return result if result["parties"] else None


def merge_additional_info_provider(release_json, provider_data):
    if not provider_data:
        logger.info(
            "No Additional Info Provider Technical Identifier Reference data to merge"
        )
        return

    parties = release_json.setdefault("parties", [])

    for new_party in provider_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party["roles"])
            existing_party["roles"] = list(existing_roles)
        else:
            parties.append(new_party)

    logger.info(
        "Merged Additional Info Provider Technical Identifier Reference data for %s parties",
        len(provider_data["parties"]),
    )
