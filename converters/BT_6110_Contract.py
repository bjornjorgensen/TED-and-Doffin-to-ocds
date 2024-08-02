# converters/BT_6110_Contract.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_contract_eu_funds_details(xml_content):
    """
    Parse the XML content to extract contract EU funds details.

    This function processes the BT-6110-Contract business term, which represents
    further information about the Union programme or project used to at least
    partially finance the procurement.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed contract EU funds details in the format:
              {
                  "contracts": [
                      {
                          "id": "contract_id",
                          "finance": [
                              {
                                  "description": "funding_description"
                              }
                          ],
                          "awardID": "award_id"
                      }
                  ]
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
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

    result = {"contracts": []}

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for contract in settled_contracts:
        contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)
        funding_descriptions = contract.xpath("efac:Funding/cbc:Description/text()", namespaces=namespaces)
        
        if contract_id and funding_descriptions:
            contract_data = {
                "id": contract_id[0],
                "finance": [{"description": desc} for desc in funding_descriptions],
            }
            
            # Find the corresponding LotResult to get the awardID
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id[0]}']", namespaces=namespaces)
            if lot_result:
                award_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
                if award_id:
                    contract_data["awardID"] = award_id[0]
            
            result["contracts"].append(contract_data)

    return result if result["contracts"] else None

def merge_contract_eu_funds_details(release_json, eu_funds_details):
    """
    Merge the parsed contract EU funds details into the main OCDS release JSON.

    This function updates the existing contracts in the release JSON with the
    EU funds details. If a contract doesn't exist, it adds a new contract to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        eu_funds_details (dict): The parsed contract EU funds details to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not eu_funds_details:
        logger.warning("BT-6110-Contract: No contract EU funds details to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])
    
    for new_contract in eu_funds_details["contracts"]:
        existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
        if existing_contract:
            existing_contract.setdefault("finance", []).extend(new_contract["finance"])
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(f"BT-6110-Contract: Merged contract EU funds details for {len(eu_funds_details['contracts'])} contracts")