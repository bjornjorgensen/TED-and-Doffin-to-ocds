# converters/OPP_080_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_kilometers_public_transport(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"contracts": []}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)[0]
        kilometers = lot_tender.xpath("efbc:PublicTransportationCumulatedDistance/text()", namespaces=namespaces)
        
        if kilometers:
            settled_contract = root.xpath(f"//efac:NoticeResult/efac:SettledContract[efac:LotTender/cbc:ID[@schemeName='tender']/text()='{tender_id}']", namespaces=namespaces)[0]
            contract_id = settled_contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)[0]
            
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']", namespaces=namespaces)[0]
            award_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[0]
            
            result["contracts"].append({
                "id": contract_id,
                "publicPassengerTransportServicesKilometers": int(kilometers[0]),
                "awardID": award_id
            })

    return result if result["contracts"] else None

def merge_kilometers_public_transport(release_json, kilometers_data):
    if not kilometers_data:
        logger.warning("No Kilometers Public Transport data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])
    
    for new_contract in kilometers_data["contracts"]:
        existing_contract = next((contract for contract in existing_contracts if contract["id"] == new_contract["id"]), None)
        if existing_contract:
            existing_contract["publicPassengerTransportServicesKilometers"] = new_contract["publicPassengerTransportServicesKilometers"]
            existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(f"Merged Kilometers Public Transport for {len(kilometers_data['contracts'])} contracts")