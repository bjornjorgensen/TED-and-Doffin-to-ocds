# converters/BT_630_Lot.py

import logging
from lxml import etree
from utils.date_utils import EndDate

logger = logging.getLogger(__name__)

def parse_lot_tender_period(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        end_date = lot.xpath(".//efac:InterestExpressionReceptionPeriod/cbc:EndDate/text()", namespaces=namespaces)
        end_time = lot.xpath(".//efac:InterestExpressionReceptionPeriod/cbc:EndTime/text()", namespaces=namespaces)
        
        logger.debug(f"Lot ID: {lot_id}")
        logger.debug(f"End Date: {end_date}")
        logger.debug(f"End Time: {end_time}")
        
        if end_date:
            end_datetime = f"{end_date[0]}T{end_time[0]}" if end_time else end_date[0]
            logger.debug(f"End DateTime before EndDate function: {end_datetime}")
            iso_end_datetime = EndDate(end_datetime)
            logger.debug(f"ISO End DateTime after EndDate function: {iso_end_datetime}")
            
            lot_data = {
                "id": lot_id,
                "tenderPeriod": {
                    "endDate": iso_end_datetime
                }
            }
            result["tender"]["lots"].append(lot_data)

    logger.debug(f"Final result: {result}")
    return result if result["tender"]["lots"] else None

def merge_lot_tender_period(release_json, lot_tender_period_data):
    if not lot_tender_period_data:
        logger.warning("No lot tender period data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in lot_tender_period_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.update(new_lot)
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged lot tender period data for {len(lot_tender_period_data['tender']['lots'])} lots")