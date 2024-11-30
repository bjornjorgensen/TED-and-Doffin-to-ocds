# converters/opt_301_lot_reviewinfo.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_info_provider_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": []}

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AppealTerms/cac:AppealInformationParty/cac:PartyIdentification/cbc:ID"
    review_info_ids = root.xpath(xpath_query, namespaces=namespaces)

    for review_info_id in review_info_ids:
        party = {"id": review_info_id.text, "roles": ["reviewContactPoint"]}
        result["parties"].append(party)

    return result if result["parties"] else None


def merge_review_info_provider_identifier(release_json, review_info_data) -> None:
    if not review_info_data:
        return

    parties = release_json.setdefault("parties", [])

    for new_party in review_info_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "reviewContactPoint" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewContactPoint")
        else:
            parties.append(new_party)

    logger.info("Merged %d review info provider(s)", len(review_info_data["parties"]))
