# converters/OPT_301_Part_Mediator.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_part_mediator(xml_content):
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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:MediationParty/cac:PartyIdentification/cbc:ID"
    mediator_ids = root.xpath(xpath, namespaces=namespaces)

    for mediator_id in mediator_ids:
        result["parties"].append({"id": mediator_id.text, "roles": ["mediationBody"]})

    return result if result["parties"] else None


def merge_part_mediator(release_json, mediator_data):
    if not mediator_data:
        logger.warning("No Part Mediator data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in mediator_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    logger.info(
        f"Merged Part Mediator data for {len(mediator_data['parties'])} parties"
    )
