# converters/BT_27_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_bt_27_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    amount_element = root.xpath("//cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount", namespaces=namespaces)
    
    if amount_element:
        amount_element = amount_element[0]
        amount = float(amount_element.text)
        currency = amount_element.get('currencyID')

        result["tender"]["value"] = {
            "amount": amount,
            "currency": currency
        }

    return result

def merge_bt_27_procedure(release_json, bt_27_procedure_data):
    if "value" in bt_27_procedure_data["tender"]:
        release_json.setdefault("tender", {})["value"] = bt_27_procedure_data["tender"]["value"]
        logger.info("Merged BT-27-Procedure Estimated Value data")
    else:
        logger.info("No BT-27-Procedure Estimated Value data to merge")