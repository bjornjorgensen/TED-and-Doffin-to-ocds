# converters/BT_721_Contract.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_contract_title(xml_content):
    """
    Parse the XML content to extract contract title information.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed contract title data.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes 
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
    
    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)
        contract_title = settled_contract.xpath("cbc:Title/text()", namespaces=namespaces)

        if contract_id and contract_title:
            contract = {
                "id": contract_id[0],
                "title": contract_title[0]
            }

            # Find corresponding LotResult
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id[0]}']", namespaces=namespaces)
            if lot_result:
                result_id = lot_result[0].xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
                if result_id:
                    contract["awardID"] = result_id[0]

            result["contracts"].append(contract)

    return result if result["contracts"] else None

def merge_contract_title(release_json, contract_title_data):
    """
    Merge the parsed contract title data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        contract_title_data (dict): The parsed contract title data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not contract_title_data:
        logger.warning("No contract title data to merge")
        return

    if "contracts" not in release_json:
        release_json["contracts"] = []

    for new_contract in contract_title_data["contracts"]:
        existing_contract = next((contract for contract in release_json["contracts"] if contract["id"] == new_contract["id"]), None)
        if existing_contract:
            existing_contract.update(new_contract)
        else:
            release_json["contracts"].append(new_contract)

    logger.info(f"Merged contract title data for {len(contract_title_data['contracts'])} contracts")