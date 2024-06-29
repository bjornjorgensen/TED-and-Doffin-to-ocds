# converters/BT_6110_Contract.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_contract_eu_funds_details(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"contracts": []}

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    for contract in settled_contracts:
        contract_id_elements = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)
        if not contract_id_elements:
            logger.warning("Contract ID not found for a SettledContract")
            continue
        contract_id = contract_id_elements[0]
        
        funding_descriptions = contract.xpath("efac:Funding/cbc:FundingProgram/text()", namespaces=namespaces)

        lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id}']", namespaces=namespaces)
        award_ids = []
        for lot in lot_results:
            award_id_elements = lot.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
            if award_id_elements:
                award_ids.append(award_id_elements[0])
            else:
                logger.warning(f"Award ID not found for contract {contract_id}")

        if funding_descriptions:
            contract_data = {
                "id": contract_id,
                "financingParty": "European Union"
            }
            if award_ids:
                if len(award_ids) == 1:
                    contract_data["awardID"] = award_ids[0]
                else:
                    contract_data["awardIDs"] = award_ids
            result["contracts"].append(contract_data)

    return result if result["contracts"] else None

def merge_contract_eu_funds_details(release_json, contract_eu_funds_data):
    if not contract_eu_funds_data:
        logger.warning("No Contract EU Funds data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])
    for new_contract in contract_eu_funds_data["contracts"]:
        existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
        if existing_contract:
            existing_contract["financingParty"] = new_contract["financingParty"]
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
            elif "awardIDs" in new_contract:
                existing_contract["awardIDs"] = new_contract["awardIDs"]
        else:
            existing_contracts.append(new_contract)

    logger.info(f"Merged Contract EU Funds details for {len(contract_eu_funds_data['contracts'])} contracts")