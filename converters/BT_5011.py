# converters/BT_5011.py
from lxml import etree

def parse_contract_eu_funds_financing_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }
    
    result = {
        "parties": [],
        "contracts": []
    }

    # Add European Union as a party
    eu_party = {
        "id": "EU-1",  # You might want to use a more sophisticated ID generation method
        "name": "European Union",
        "roles": ["funder"]
    }

    # Parse Contract EU Funds Financing Identifier
    notice_result = root.xpath("/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult", namespaces=namespaces)
    if notice_result:
        notice_result = notice_result[0]
        settled_contracts = notice_result.xpath("efac:SettledContract", namespaces=namespaces)

        for settled_contract in settled_contracts:
            contract_id = settled_contract.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            
            funding_elements = settled_contract.xpath("efac:Funding/efbc:FinancingIdentifier/text()", namespaces=namespaces)
            
            contract = {
                "id": contract_id
            }

            if funding_elements:
                contract["finance"] = []
                for funding_id in funding_elements:
                    finance = {
                        "id": funding_id,
                        "financingParty": {
                            "id": eu_party["id"],
                            "name": eu_party["name"]
                        }
                    }
                    contract["finance"].append(finance)

                # Only add the EU party if we actually have financing
                if "parties" not in result:
                    result["parties"] = []
                result["parties"].append(eu_party)

            # Get related LotResults
            lot_results = notice_result.xpath(f"efac:LotResult[efac:SettledContract/cbc:ID/text()='{contract_id}']", namespaces=namespaces)
            if len(lot_results) == 1:
                contract["awardID"] = lot_results[0].xpath("cbc:ID/text()", namespaces=namespaces)[0]
            elif len(lot_results) > 1:
                contract["awardIDs"] = [lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0] for lot_result in lot_results]

            result["contracts"].append(contract)

    return result if result["contracts"] else None

def merge_contract_eu_funds_financing_identifier(release_json, contract_eu_funds_data):
    if contract_eu_funds_data:
        # Merge parties
        if "parties" in contract_eu_funds_data:
            existing_parties = release_json.setdefault("parties", [])
            eu_party = next((party for party in contract_eu_funds_data["parties"] if party["name"] == "European Union"), None)
            if eu_party:
                existing_eu_party = next((party for party in existing_parties if party.get("name") == "European Union"), None)
                if existing_eu_party:
                    existing_eu_party["roles"] = list(set(existing_eu_party.get("roles", []) + eu_party["roles"]))
                else:
                    existing_parties.append(eu_party)

        # Merge contracts
        existing_contracts = release_json.setdefault("contracts", [])
        for new_contract in contract_eu_funds_data["contracts"]:
            existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
            if existing_contract:
                if "finance" in new_contract:
                    existing_finance = existing_contract.setdefault("finance", [])
                    for new_finance in new_contract["finance"]:
                        existing_finance_item = next((item for item in existing_finance if item["id"] == new_finance["id"]), None)
                        if existing_finance_item:
                            existing_finance_item.update(new_finance)
                        else:
                            existing_finance.append(new_finance)
                
                if "awardID" in new_contract:
                    existing_contract["awardID"] = new_contract["awardID"]
                if "awardIDs" in new_contract:
                    existing_contract["awardIDs"] = new_contract["awardIDs"]
            else:
                existing_contracts.append(new_contract)
