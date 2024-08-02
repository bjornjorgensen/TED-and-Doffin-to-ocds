# converters/BT_44_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_prize_rank(xml_content):
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

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        prizes = lot.xpath(".//cac:AwardingTerms/cac:Prize", namespaces=namespaces)
        
        if prizes:
            lot_data = {
                "id": lot_id,
                "designContest": {
                    "prizes": {
                        "details": []
                    }
                }
            }
            
            for i, prize in enumerate(prizes):
                rank_code = prize.xpath("cbc:RankCode/text()", namespaces=namespaces)
                prize_data = {"id": str(i)}
                if rank_code:
                    prize_data["rank"] = int(rank_code[0])
                lot_data["designContest"]["prizes"]["details"].append(prize_data)
            
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_prize_rank(release_json, prize_rank_data):
    if not prize_rank_data:
        logger.warning("No Prize Rank data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in prize_rank_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("designContest", {}).setdefault("prizes", {})["details"] = new_lot["designContest"]["prizes"]["details"]
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Prize Rank data for {len(prize_rank_data['tender']['lots'])} lots")