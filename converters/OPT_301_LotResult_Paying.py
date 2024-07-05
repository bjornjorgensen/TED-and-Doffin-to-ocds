# converters/OPT_301_LotResult_Paying.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_lotresult_paying(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/cac:PayerParty/cac:PartyIdentification/cbc:ID"
    payer_party_ids = root.xpath(xpath, namespaces=namespaces)

    result = {"parties": []}

    for party_id in payer_party_ids:
        result["parties"].append({
            "id": party_id.text,
            "roles": ["payer"]
        })

    return result if result["parties"] else None

def merge_lotresult_paying(release_json, paying_data):
    if not paying_data:
        logger.warning("No LotResult Paying data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in paying_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    logger.info(f"Merged LotResult Paying data for {len(paying_data['parties'])} parties")