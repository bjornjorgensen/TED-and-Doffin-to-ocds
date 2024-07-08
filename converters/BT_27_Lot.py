# converters/BT_27_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_bt_27_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)
        amount_element = lot_element.xpath("cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount", namespaces=namespaces)
        
        if lot_id and amount_element:
            lot_id = lot_id[0]
            amount_element = amount_element[0]
            amount = float(amount_element.text)
            currency = amount_element.get('currencyID')

            lot = {
                "id": lot_id,
                "value": {
                    "amount": amount,
                    "currency": currency
                }
            }
            
            result["tender"]["lots"].append(lot)
        else:
            logger.warning(f"Missing data for lot {lot_id}")

    return result

def merge_bt_27_lot(release_json, bt_27_data):
    if not bt_27_data["tender"]["lots"]:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in bt_27_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot["value"] = new_lot["value"]
        else:
            existing_lots.append(new_lot)
    
    logger.info(f"Merged BT-27 data for {len(bt_27_data['tender']['lots'])} lots")