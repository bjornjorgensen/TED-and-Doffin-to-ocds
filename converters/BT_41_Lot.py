# converters/BT_41_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_following_contract(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        followup_contract_indicator = lot.xpath(".//cac:AwardingTerms/cbc:FollowupContractIndicator/text()", namespaces=namespaces)
        
        if followup_contract_indicator and followup_contract_indicator[0].lower() == 'true':
            lot_data = {
                "id": lot_id,
                "designContest": {
                    "followUpContracts": True
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_lot_following_contract(release_json, lot_following_contract_data):
    if not lot_following_contract_data:
        logger.warning("No lot following contract data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in lot_following_contract_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("designContest", {}).update(new_lot["designContest"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged lot following contract data for {len(lot_following_contract_data['tender']['lots'])} lots")