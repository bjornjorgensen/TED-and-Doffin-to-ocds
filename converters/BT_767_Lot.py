# converters/BT_767_Lot.py

import logging
from lxml import etree
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)

def parse_electronic_auction(xml_content: Union[str, bytes]) -> Optional[Dict]:
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
        
    root: etree._Element = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result: Dict[str, Dict] = {"tender": {"lots": []}}

    lots: list = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id: str = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        auction_indicator: list = lot.xpath(
            "cac:TenderingProcess/cac:AuctionTerms/cbc:AuctionConstraintIndicator/text()",
            namespaces=namespaces
        )
        
        if auction_indicator:
            result["tender"]["lots"].append({
                "id": lot_id,
                "techniques": {
                    "hasElectronicAuction": auction_indicator[0].lower() == 'true'
                }
            })

    return result if result["tender"]["lots"] else None

def merge_electronic_auction(release_json: Dict, electronic_auction_data: Optional[Dict]) -> None:
    if not electronic_auction_data:
        logger.warning("No electronic auction data to merge")
        return

    tender: Dict = release_json.setdefault("tender", {})
    existing_lots: list = tender.setdefault("lots", [])
    
    for new_lot in electronic_auction_data["tender"]["lots"]:
        existing_lot: Optional[Dict] = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("techniques", {}).update(new_lot["techniques"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged electronic auction data for {len(electronic_auction_data['tender']['lots'])} lots")