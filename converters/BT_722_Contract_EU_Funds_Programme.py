# converters/BT_722_Contract_EU_Funds_Programme.py
from lxml import etree

def parse_contract_eu_funds_programme(xml_content):
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
        contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)
        funding_programmes = contract.xpath("efac:Funding/cbc:FundingProgramCode[@listName='eu-programme']/text()", namespaces=namespaces)
        
        if contract_id:
            contract_data = {
                'id': contract_id[0]
            }
            
            if funding_programmes:
                contract_data['finance'] = [{'title': programme} for programme in funding_programmes]
            
            # Find corresponding LotResults
            lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']='{contract_id[0]}']", namespaces=namespaces)
            award_ids = [lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0] for lot_result in lot_results]
            
            if len(award_ids) == 1:
                contract_data['awardID'] = award_ids[0]
            elif len(award_ids) > 1:
                contract_data['awardIDs'] = award_ids
            
            result[contract_id[0]] = contract_data

    return result

def merge_contract_eu_funds_programme(release_json, contract_eu_funds_data):
    if contract_eu_funds_data:
        contracts = release_json.setdefault("contracts", [])

        for contract_id, contract_data in contract_eu_funds_data.items():
            contract = next((c for c in contracts if c.get("id") == contract_id), None)
            if contract:
                # Update existing contract
                if 'finance' in contract_data:
                    existing_finance = contract.get('finance', [])
                    for new_finance in contract_data['finance']:
                        if new_finance not in existing_finance:
                            existing_finance.append(new_finance)
                    if existing_finance:
                        contract['finance'] = existing_finance
                    elif 'finance' in contract:
                        del contract['finance']
                if 'awardID' in contract_data:
                    contract['awardID'] = contract_data['awardID']
                if 'awardIDs' in contract_data:
                    contract['awardIDs'] = contract_data['awardIDs']
            else:
                # Add new contract
                contracts.append(contract_data)

    return release_json