import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_penalties_and_rewards(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"tender": {"lots": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    for lot_tender in lot_tenders:
        lot_id_elements = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        if not lot_id_elements:
            raise ValueError("Lot ID is missing for a LotTender")
        
        lot_id = lot_id_elements[0]
        penalties_and_rewards = lot_tender.xpath("efac:ContractTerm[efbc:TermCode='pena-rewa']/efbc:TermDescription/text()", namespaces=namespaces)
        if penalties_and_rewards:
            lot = {
                "id": lot_id,
                "contractTerms": {
                    "penaltiesAndRewards": penalties_and_rewards[0]
                }
            }
            result["tender"]["lots"].append(lot)

    return result if result["tender"]["lots"] else None

def merge_penalties_and_rewards(release_json, penalties_and_rewards_data):
    if not penalties_and_rewards_data:
        logger.warning("No Penalties and Rewards data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in penalties_and_rewards_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(new_lot["contractTerms"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Penalties and Rewards data for {len(penalties_and_rewards_data['tender']['lots'])} lots")