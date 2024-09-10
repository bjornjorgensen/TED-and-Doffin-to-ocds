# converters/OPT_301_Part_DocProvider.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_part_docprovider(xml_content):
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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:DocumentProviderParty/cac:PartyIdentification/cbc:ID"
    docprovider_party_ids = root.xpath(xpath, namespaces=namespaces)

    result = {"parties": []}

    for party_id in docprovider_party_ids:
        result["parties"].append(
            {"id": party_id.text, "roles": ["processContactPoint"]}
        )

    return result if result["parties"] else None


def merge_part_docprovider(release_json, docprovider_data):
    if not docprovider_data:
        logger.warning("No Part Document Provider data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in docprovider_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    logger.info(
        f"Merged Part Document Provider data for {len(docprovider_data['parties'])} parties"
    )
