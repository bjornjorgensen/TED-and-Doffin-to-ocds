# converters/opt_301_lot_revieworg.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_organization_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": []}

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AppealTerms/cac:AppealReceiverParty/cac:PartyIdentification/cbc:ID"
    review_org_ids = root.xpath(xpath_query, namespaces=namespaces)

    for review_org_id in review_org_ids:
        party = {"id": review_org_id.text, "roles": ["reviewBody"]}
        result["parties"].append(party)

    return result if result["parties"] else None


def merge_review_organization_identifier(release_json, review_org_data) -> None:
    if not review_org_data:
        return

    parties = release_json.setdefault("parties", [])

    for new_party in review_org_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "reviewBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewBody")
        else:
            parties.append(new_party)

    logger.info("Merged %d review organization(s)", len(review_org_data["parties"]))
