# converters/OPP_034_Tender.py

from lxml import etree
import logging

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
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        
        rewards_penalties = lot_tender.xpath("efac:ContractTerm[efbc:TermCode/@listName='rewards-penalties']/efbc:TermDescription/text()", namespaces=namespaces)
        
        if rewards_penalties:
            result["tender"]["lots"].append({
                "id": lot_id,
                "contractTerms": {
                    "rewardsAndPenalties": rewards_penalties[0]
                }
            })

    return result if result["tender"]["lots"] else None

def merge_penalties_and_rewards(release_json, penalties_and_rewards_data):
    if not penalties_and_rewards_data:
        logger.warning("No Penalties and Rewards data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in penalties_and_rewards_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(new_lot["contractTerms"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Penalties and Rewards for {len(penalties_and_rewards_data['tender']['lots'])} lots")