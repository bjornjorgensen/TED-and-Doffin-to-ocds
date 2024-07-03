# converters/BT_145_Contract.py

import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)

def parse_contract_conclusion_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    }
    
    contracts_data = []
    
    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for contract in settled_contracts:
        contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)[0]
        issue_date = contract.xpath("cbc:IssueDate/text()", namespaces=namespaces)
        
        if issue_date:
            iso_date = convert_to_iso_format(issue_date[0])
            
            # Find the corresponding LotResult to get the award ID
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']", namespaces=namespaces)
            award_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0] if lot_result else None
            
            contracts_data.append({
                "id": contract_id,
                "dateSigned": iso_date,
                "awardID": award_id
            })
    
    return contracts_data if contracts_data else None

def convert_to_iso_format(date_string):
    # Split the date string and timezone
    date_part, _, tz_part = date_string.partition('+')
    
    # Parse the date part
    date = datetime.strptime(date_part, "%Y-%m-%d")
    
    # Set the time to 23:59:59
    date = date.replace(hour=23, minute=59, second=59)
    
    # Format the datetime with the original timezone
    return f"{date.isoformat()}+{tz_part}"

def merge_contract_conclusion_date(release_json, contracts_data):
    if contracts_data:
        if "contracts" not in release_json:
            release_json["contracts"] = []
        
        for contract_data in contracts_data:
            existing_contract = next((contract for contract in release_json["contracts"] if contract["id"] == contract_data["id"]), None)
            if existing_contract:
                existing_contract.update(contract_data)
            else:
                release_json["contracts"].append(contract_data)