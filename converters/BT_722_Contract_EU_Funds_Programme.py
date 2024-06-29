# converters/BT_722_Contract_EU_Funds_Programme.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_contract_eu_funds_programme(xml_content):
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
            award_ids = []
            for lot_result in lot_results:
                award_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
                if award_id:
                    award_ids.append(award_id[0])
                else:
                    logger.warning(f"Award ID not found for contract {contract_id[0]}")

            if award_ids:
                if len(award_ids) == 1:
                    contract_data['awardID'] = award_ids[0]
                else:
                    contract_data['awardIDs'] = award_ids

            result["contracts"].append(contract_data)

    return result if result["contracts"] else None

def merge_contract_eu_funds_programme(release_json, contract_eu_funds_data):
    if not contract_eu_funds_data:
        logger.warning("No Contract EU Funds Programme data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])
    for new_contract in contract_eu_funds_data["contracts"]:
        existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
        if existing_contract:
            if "finance" in new_contract:
                existing_contract["finance"] = new_contract["finance"]
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
            elif "awardIDs" in new_contract:
                existing_contract["awardIDs"] = new_contract["awardIDs"]
        else:
            existing_contracts.append(new_contract)

    logger.info(f"Merged Contract EU Funds Programme for {len(contract_eu_funds_data['contracts'])} contracts")