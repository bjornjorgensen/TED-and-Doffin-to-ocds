# converters/BT_131_Lot.py

import logging
from lxml import etree
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)

def parse_deadline_receipt_tenders(xml_content):
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
    logger.info(f"Found {len(lots)} lots in XML")
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        if not lot_id:
            logger.warning("Lot ID not found, skipping this lot")
            continue
        lot_id = lot_id[0]
        
        end_date = lot.xpath("cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndDate/text()", namespaces=namespaces)
        end_time = lot.xpath("cac:TenderingProcess/cac:TenderSubmissionDeadlinePeriod/cbc:EndTime/text()", namespaces=namespaces)
        
        logger.info(f"Processing lot {lot_id}: EndDate={end_date}, EndTime={end_time}")
        
        if end_date:
            try:
                date_str = end_date[0]
                time_str = end_time[0] if end_time else "23:59:59"
                
                # Combine date and time
                datetime_str = f"{date_str.split('+')[0]}T{time_str}"
                
                # Parse the datetime string
                dt = datetime.fromisoformat(datetime_str)
                
                # Add timezone information if present in the original string
                if '+' in date_str:
                    tz_offset = date_str.split('+')[1]
                    dt = dt.replace(tzinfo=timezone(timedelta(hours=int(tz_offset.split(':')[0]), minutes=int(tz_offset.split(':')[1]))))
                else:
                    dt = dt.replace(tzinfo=timezone.utc)
                
                iso_date = dt.isoformat()
                
                result["tender"]["lots"].append({
                    "id": lot_id,
                    "tenderPeriod": {
                        "endDate": iso_date
                    }
                })
                logger.info(f"Successfully processed lot {lot_id} with endDate: {iso_date}")
            except ValueError as e:
                logger.error(f"Error parsing deadline for lot {lot_id}: {str(e)}")
        else:
            logger.warning(f"No EndDate found for lot {lot_id}, skipping this lot")

    logger.info(f"Processed {len(result['tender']['lots'])} lots in total")
    return result if result["tender"]["lots"] else None

def merge_deadline_receipt_tenders(release_json, deadline_data):
    if not deadline_data:
        logger.warning("No Deadline Receipt Tenders data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in deadline_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("tenderPeriod", {}).update(new_lot["tenderPeriod"])
            logger.info(f"Updated existing lot {new_lot['id']} with tenderPeriod data")
        else:
            existing_lots.append(new_lot)
            logger.info(f"Added new lot {new_lot['id']} with tenderPeriod data")

    logger.info(f"Merged Deadline Receipt Tenders data for {len(deadline_data['tender']['lots'])} lots")