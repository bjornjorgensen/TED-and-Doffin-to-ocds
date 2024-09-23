# converters/OPT_300_Procedure_SProvider.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_procedure_sprovider(xml_content):
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

    xpath = "/*/cac:ContractingParty/cac:Party/cac:ServiceProviderParty/cac:Party/cac:PartyIdentification/cbc:ID"
    sprovider_ids = root.xpath(xpath, namespaces=namespaces)

    result = {"parties": []}

    for sprovider_id in sprovider_ids:
        org_id = sprovider_id.text
        org_xpath = f"//efac:Organizations/efac:Organization/efac:Company[cac:PartyIdentification/cbc:ID/text()='{org_id}']"
        org = root.xpath(org_xpath, namespaces=namespaces)

        if org:
            org_name = org[0].xpath(
                "cac:PartyName/cbc:Name/text()", namespaces=namespaces,
            )[0]
            result["parties"].append({"id": org_id, "name": org_name})

    return result if result["parties"] else None


def merge_procedure_sprovider(release_json, sprovider_data):
    if not sprovider_data:
        logger.warning("No Procedure Service Provider data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in sprovider_data["parties"]:
        if party["id"] in existing_parties:
            existing_parties[party["id"]]["name"] = party["name"]
        else:
            release_json.setdefault("parties", []).append(party)

    logger.info(
        f"Merged Procedure Service Provider data for {len(sprovider_data['parties'])} parties",
    )
