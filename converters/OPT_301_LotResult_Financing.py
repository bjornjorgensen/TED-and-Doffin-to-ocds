# converters/OPT_301_LotResult_Financing.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_lotresult_financing(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/cac:FinancingParty/cac:PartyIdentification/cbc:ID"
    financing_party_ids = root.xpath(xpath, namespaces=namespaces)

    result = {"parties": []}

    for party_id in financing_party_ids:
        result["parties"].append({"id": party_id.text, "roles": ["funder"]})

    return result if result["parties"] else None


def merge_lotresult_financing(release_json, financing_data):
    if not financing_data:
        logger.warning("No LotResult Financing data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in financing_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    logger.info(
        f"Merged LotResult Financing data for {len(financing_data['parties'])} parties"
    )
