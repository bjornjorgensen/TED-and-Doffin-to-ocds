# converters/BT_5011_Contract.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_eu_funds_financing_identifier(xml_content):
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

    result = {"parties": [], "contracts": []}

    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract",
        namespaces=namespaces,
    )

    for contract in settled_contracts:
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )[0]
        funding_elements = contract.xpath("efac:Funding", namespaces=namespaces)

        contract_finance = []
        for funding in funding_elements:
            financing_identifier = funding.xpath(
                "efbc:FinancingIdentifier/text()",
                namespaces=namespaces,
            )

            if financing_identifier:
                finance_item = {
                    "id": financing_identifier[0],
                    "financingParty": {"name": "European Union"},
                }
                contract_finance.append(finance_item)

        if contract_finance:
            result["contracts"].append({"id": contract_id, "finance": contract_finance})

    if result["contracts"]:
        result["parties"].append({"name": "European Union", "roles": ["funder"]})

    return result if result["parties"] else None


def merge_contract_eu_funds_financing_identifier(
    release_json,
    contract_eu_funds_financing_identifier_data,
):
    if not contract_eu_funds_financing_identifier_data:
        logger.warning("No Contract EU Funds Financing Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    eu_party = next(
        (party for party in existing_parties if party.get("name") == "European Union"),
        None,
    )

    if eu_party:
        if "funder" not in eu_party.get("roles", []):
            eu_party.setdefault("roles", []).append("funder")
    else:
        new_party = contract_eu_funds_financing_identifier_data["parties"][0]
        new_party["id"] = str(len(existing_parties) + 1)
        existing_parties.append(new_party)

    eu_party = next(
        party for party in existing_parties if party.get("name") == "European Union"
    )

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_eu_funds_financing_identifier_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_finance = existing_contract.setdefault("finance", [])
            for new_finance in new_contract["finance"]:
                existing_finance_item = next(
                    (
                        item
                        for item in existing_finance
                        if item["id"] == new_finance["id"]
                    ),
                    None,
                )
                if existing_finance_item:
                    existing_finance_item["financingParty"] = {
                        "id": eu_party["id"],
                        "name": "European Union",
                    }
                else:
                    new_finance["financingParty"]["id"] = eu_party["id"]
                    existing_finance.append(new_finance)
        else:
            for finance_item in new_contract["finance"]:
                finance_item["financingParty"]["id"] = eu_party["id"]
            existing_contracts.append(new_contract)

    logger.info(
        f"Merged Contract EU Funds Financing Identifier data for {len(contract_eu_funds_financing_identifier_data['contracts'])} contracts",
    )
