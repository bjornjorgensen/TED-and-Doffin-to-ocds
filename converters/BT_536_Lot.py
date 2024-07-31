# converters/BT_536_Lot.py

import logging
from lxml import etree
from utils.date_utils import StartDate

logger = logging.getLogger(__name__)

def parse_lot_start_date(xml_content):
    logger.info("Starting parse_lot_start_date function")
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
    logger.info(f"Found {len(lots)} lots")
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        start_date = lot.xpath("cac:ProcurementProject/cac:PlannedPeriod/cbc:StartDate/text()", namespaces=namespaces)
        
        logger.info(f"Processing lot {lot_id}")
        logger.info(f"Start date found: {start_date}")
        
        if start_date:
            try:
                formatted_start_date = StartDate(start_date[0])
                lot_data = {
                    "id": lot_id,
                    "contractPeriod": {
                        "startDate": formatted_start_date
                    }
                }
                result["tender"]["lots"].append(lot_data)
                logger.info(f"Added lot data: {lot_data}")
            except ValueError as e:
                logger.error(f"Error formatting start date for lot {lot_id}: {str(e)}")
        else:
            logger.warning(f"No start date found for lot {lot_id}")

    logger.info(f"Final result: {result}")
    return result if result["tender"]["lots"] else None

def merge_lot_start_date(release_json, lot_start_date_data):
    logger.info(f"Starting merge_lot_start_date function")
    logger.info(f"Merging lot start date data: {lot_start_date_data}")
    if not lot_start_date_data:
        logger.warning("No lot start date data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_start_date_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractPeriod", {}).update(new_lot["contractPeriod"])
            logger.info(f"Updated existing lot: {existing_lot}")
        else:
            existing_lots.append(new_lot)
            logger.info(f"Added new lot: {new_lot}")

    logger.info(f"Final release_json after merge: {release_json}")