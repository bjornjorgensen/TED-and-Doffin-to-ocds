# converters/BT_537_Lot.py

from lxml import etree
from utils.date_utils import EndDate

def parse_lot_duration_end_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        end_date = lot_element.xpath("cac:ProcurementProject/cac:PlannedPeriod/cbc:EndDate/text()", namespaces=namespaces)
        
        if end_date:
            try:
                iso_end_date = EndDate(end_date[0])
                lot = {
                    "id": lot_id,
                    "contractPeriod": {
                        "endDate": iso_end_date
                    }
                }
                result["tender"]["lots"].append(lot)
            except ValueError as e:
                print(f"Warning: Invalid date format for lot {lot_id}: {str(e)}")

    return result if result["tender"]["lots"] else None

def merge_lot_duration_end_date(release_json, lot_duration_end_date_data):
    if not lot_duration_end_date_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in lot_duration_end_date_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractPeriod", {}).update(new_lot["contractPeriod"])
        else:
            existing_lots.append(new_lot)