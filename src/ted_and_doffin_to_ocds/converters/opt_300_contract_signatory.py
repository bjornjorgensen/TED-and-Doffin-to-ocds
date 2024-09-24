# converters/OPT_300_Contract_Signatory.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_contract_signatory(xml_content):
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

    result = {"parties": [], "awards": []}

    xpath = "//efac:noticeResult/efac:SettledContract/cac:Signatoryparty/cac:partyIdentification/cbc:ID"
    signatory_ids = root.xpath(xpath, namespaces=namespaces)

    for signatory_id in signatory_ids:
        org_id = signatory_id.text
        org_xpath = f"//efac:organizations/efac:organization/efac:company[cac:partyIdentification/cbc:ID/text()='{org_id}']"
        org = root.xpath(org_xpath, namespaces=namespaces)

        if org:
            org_name = org[0].xpath(
                "cac:partyName/cbc:Name/text()",
                namespaces=namespaces,
            )[0]
            result["parties"].append(
                {"id": org_id, "name": org_name, "roles": ["buyer"]},
            )

        # Find the corresponding SettledContract
        contract_xpath = f"//efac:noticeResult/efac:SettledContract[cac:Signatoryparty/cac:partyIdentification/cbc:ID/text()='{org_id}']"
        contract = root.xpath(contract_xpath, namespaces=namespaces)

        if contract:
            contract_id = contract[0].xpath(
                "cbc:ID[@schemeName='contract']/text()",
                namespaces=namespaces,
            )[0]
            award_xpath = f"//efac:noticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']/cbc:ID[@schemeName='result']/text()"
            award_ids = root.xpath(award_xpath, namespaces=namespaces)

            for award_id in award_ids:
                result["awards"].append({"id": award_id, "buyers": [{"id": org_id}]})

    return result if (result["parties"] or result["awards"]) else None


def merge_contract_signatory(release_json, signatory_data):
    if not signatory_data:
        logger.warning("No Contract Signatory data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in signatory_data.get("parties", []):
        if party["id"] in existing_parties:
            existing_parties[party["id"]]["roles"] = list(
                set(existing_parties[party["id"]].get("roles", []) + party["roles"]),
            )
        else:
            release_json.setdefault("parties", []).append(party)

    existing_awards = {
        award.get("id"): award for award in release_json.get("awards", [])
    }
    for award in signatory_data.get("awards", []):
        if award["id"] in existing_awards:
            existing_buyers = {
                buyer["id"]: buyer
                for buyer in existing_awards[award["id"]].get("buyers", [])
            }
            for buyer in award["buyers"]:
                if buyer["id"] not in existing_buyers:
                    existing_awards[award["id"]].setdefault("buyers", []).append(buyer)
        else:
            release_json.setdefault("awards", []).append(award)

    logger.info(
        "Merged Contract Signatory data for %d parties and %d awards",
        len(signatory_data.get("parties", [])),
        len(signatory_data.get("awards", [])),
    )
