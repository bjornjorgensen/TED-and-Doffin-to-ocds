# converters/BT_150_Contract.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_contract_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    contracts = []

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)
        contract_reference = settled_contract.xpath("efac:ContractReference/cbc:ID/text()", namespaces=namespaces)
        
        if contract_id and contract_reference:
            # Find the corresponding LotResult
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id[0]}']", namespaces=namespaces)
            award_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces) if lot_result else None

            contract = {
                "id": contract_id[0],
                "identifiers": [
                    {
                        "id": contract_reference[0],
                        "scheme": "NL-TENDERNED"  # Default scheme, you might want to make this configurable
                    }
                ]
            }
            
            if award_id:
                contract["awardID"] = award_id[0]

            contracts.append(contract)

    return {"contracts": contracts} if contracts else None

def merge_contract_identifier(release_json, contract_identifier_data):
    if not contract_identifier_data:
        logger.warning("No Contract Identifier data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])
    
    for new_contract in contract_identifier_data["contracts"]:
        existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
        if existing_contract:
            existing_contract.setdefault("identifiers", []).extend(new_contract["identifiers"])
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(f"Merged Contract Identifier data for {len(contract_identifier_data['contracts'])} contracts")
    logger.debug(f"Release JSON after merging Contract Identifier data: {release_json}")