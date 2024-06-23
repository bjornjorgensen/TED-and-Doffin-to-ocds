# converters/BT_6110_Contract.py
from lxml import etree

def parse_contract_eu_funds_details(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {}

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    for contract in settled_contracts:
        contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)[0]
        funding_descriptions = contract.xpath("efac:Funding/cbc:FundingProgram/text()", namespaces=namespaces)
        
        lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id}']", namespaces=namespaces)
        award_ids = [lot.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0] for lot in lot_results]

        result[contract_id] = {
            "funding_descriptions": funding_descriptions,
            "award_ids": award_ids
        }

    return result

def merge_contract_eu_funds_details(release_json, contract_data):
    if contract_data:
        contracts = release_json.setdefault("contracts", [])

        for contract_id, data in contract_data.items():
            contract = next((c for c in contracts if c.get("id") == contract_id), None)
            if not contract:
                contract = {"id": contract_id}
                contracts.append(contract)

            if data["award_ids"]:
                if len(data["award_ids"]) == 1:
                    contract["awardID"] = data["award_ids"][0]
                else:
                    contract["awardIDs"] = data["award_ids"]

            if data["funding_descriptions"]:
                finance = contract.setdefault("finance", [])
                for description in data["funding_descriptions"]:
                    existing_finance = next((f for f in finance if f.get("description") == description), None)
                    if not existing_finance:
                        finance.append({"description": description})
                
                # Remove the "finance" key if it's empty
                if not finance:
                    contract.pop("finance", None)

    return release_json