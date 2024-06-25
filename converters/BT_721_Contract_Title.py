# converters/BT_721_Contract_Title.py
from lxml import etree

def parse_contract_title(xml_content):
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
        title = contract.xpath("cbc:Title/text()", namespaces=namespaces)
        
        if contract_id and title:
            contract_data = {
                'id': contract_id[0],
                'title': title[0]
            }
            
            # Find corresponding LotResults
            lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']='{contract_id[0]}']", namespaces=namespaces)
            award_ids = [lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0] for lot_result in lot_results]
            
            if len(award_ids) == 1:
                contract_data['awardID'] = award_ids[0]
            elif len(award_ids) > 1:
                contract_data['awardIDs'] = award_ids
            
            result[contract_id[0]] = contract_data

    return result

def merge_contract_title(release_json, contract_title_data):
    if contract_title_data:
        contracts = release_json.setdefault("contracts", [])

        for contract_id, contract_data in contract_title_data.items():
            contract = next((c for c in contracts if c.get("id") == contract_id), None)
            if contract:
                contract.update(contract_data)
            else:
                contracts.append(contract_data)

    return release_json