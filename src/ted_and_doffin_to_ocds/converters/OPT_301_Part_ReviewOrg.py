# converters/OPT_301_Part_ReviewOrg.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_part_revieworg(xml_content):
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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:AppealReceiverParty/cac:PartyIdentification/cbc:ID"
    review_org_ids = root.xpath(xpath, namespaces=namespaces)

    for review_org_id in review_org_ids:
        result["parties"].append({"id": review_org_id.text, "roles": ["reviewBody"]})

    return result if result["parties"] else None


def merge_part_revieworg(release_json, revieworg_data):
    if not revieworg_data:
        logger.warning("No Part Review Organization data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in revieworg_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    logger.info(
        f"Merged Part Review Organization data for {len(revieworg_data['parties'])} parties",
    )
