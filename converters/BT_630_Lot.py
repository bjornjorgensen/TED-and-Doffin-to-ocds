# converters/BT_630_Lot.py

import logging
from lxml import etree
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def parse_deadline_receipt_expressions(xml_content):
    """
    Parse the XML content to extract the deadline for receipt of expressions for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed deadline receipt expressions data.
        None: If no relevant data is found.
    """
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
        end_date = lot.xpath(".//efac:InterestExpressionReceptionPeriod/cbc:EndDate/text()", namespaces=namespaces)
        end_time = lot.xpath(".//efac:InterestExpressionReceptionPeriod/cbc:EndTime/text()", namespaces=namespaces)
        
        if end_date:
            try:
                date_part = end_date[0].split('+')[0]  # Remove timezone info from date
                if end_time:
                    time_part = end_time[0].split('+')[0]  # Remove timezone info from time
                    combined_datetime = f"{date_part}T{time_part}"
                else:
                    combined_datetime = f"{date_part}T23:59:59"
                
                tz_info = end_date[0].split('+')[1] if '+' in end_date[0] else 'Z'
                iso_datetime = f"{combined_datetime}+{tz_info}"
                
                lot_data = {
                    "id": lot_id,
                    "tenderPeriod": {
                        "endDate": iso_datetime
                    }
                }
                result["tender"]["lots"].append(lot_data)
            except Exception as e:
                logger.error(f"Error parsing datetime for lot {lot_id}: {str(e)}")

    return result if result["tender"]["lots"] else None

def merge_deadline_receipt_expressions(release_json, deadline_receipt_expressions_data):
    """
    Merge the parsed deadline receipt expressions data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        deadline_receipt_expressions_data (dict): The parsed deadline receipt expressions data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not deadline_receipt_expressions_data:
        logger.warning("No deadline receipt expressions data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in deadline_receipt_expressions_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("tenderPeriod", {}).update(new_lot["tenderPeriod"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged deadline receipt expressions data for {len(deadline_receipt_expressions_data['tender']['lots'])} lots")