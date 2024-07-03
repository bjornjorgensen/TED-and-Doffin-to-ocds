# converters/BT_1451_Contract.py

import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)

def parse_winner_decision_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    }
    
    awards_data = []
    
    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for contract in settled_contracts:
        contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)[0]
        award_date = contract.xpath("cbc:AwardDate/text()", namespaces=namespaces)
        
        if award_date:
            iso_date = convert_to_iso_format(award_date[0])
            
            # Find the corresponding LotResult(s) to get the award ID(s)
            lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']", namespaces=namespaces)
            
            for lot_result in lot_results:
                award_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0]
                awards_data.append({
                    "id": award_id,
                    "date": iso_date
                })
    
    return awards_data if awards_data else None

def convert_to_iso_format(date_string):
    # Split the date string and timezone
    date_part, _, tz_part = date_string.partition('+')
    
    # Parse the date part
    date = datetime.strptime(date_part, "%Y-%m-%d")
    
    # Set the time to 23:59:59
    date = date.replace(hour=23, minute=59, second=59)
    
    # Format the datetime with the original timezone
    return f"{date.isoformat()}+{tz_part}"

def merge_winner_decision_date(release_json, awards_data):
    if awards_data:
        if "awards" not in release_json:
            release_json["awards"] = []
        
        for award_data in awards_data:
            existing_award = next((award for award in release_json["awards"] if award["id"] == award_data["id"]), None)
            if existing_award:
                if "date" not in existing_award or award_data["date"] < existing_award["date"]:
                    existing_award["date"] = award_data["date"]
            else:
                release_json["awards"].append(award_data)