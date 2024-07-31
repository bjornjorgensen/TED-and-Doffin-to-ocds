# converters/BT_27_LotsGroup.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_bt_27_lots_group(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lotGroups": []}}

    lot_group_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    
    for lot_group_element in lot_group_elements:
        lot_group_id = lot_group_element.xpath("cbc:ID/text()", namespaces=namespaces)
        amount_element = lot_group_element.xpath("cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount", namespaces=namespaces)
        
        if lot_group_id and amount_element:
            lot_group_id = lot_group_id[0]
            amount_element = amount_element[0]
            amount = float(amount_element.text)
            currency = amount_element.get('currencyID')

            lot_group = {
                "id": lot_group_id,
                "maximumValue": {
                    "amount": amount,
                    "currency": currency
                }
            }
            
            result["tender"]["lotGroups"].append(lot_group)

    return result

def merge_bt_27_lots_group(release_json, bt_27_lots_group_data):
    existing_lot_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
    
    for new_lot_group in bt_27_lots_group_data["tender"]["lotGroups"]:
        existing_lot_group = next((group for group in existing_lot_groups if group["id"] == new_lot_group["id"]), None)
        if existing_lot_group:
            existing_lot_group["maximumValue"] = new_lot_group["maximumValue"]
        else:
            existing_lot_groups.append(new_lot_group)
    
    logger.info(f"Merged BT-27-LotsGroup Estimated Value data for {len(bt_27_lots_group_data['tender']['lotGroups'])} lot groups")