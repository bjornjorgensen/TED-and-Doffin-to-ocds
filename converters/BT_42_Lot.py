# converters/BT_42_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_jury_decision_binding(xml_content):
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
        binding_on_buyer_indicator = lot.xpath(".//cac:AwardingTerms/cbc:BindingOnBuyerIndicator/text()", namespaces=namespaces)
        
        if binding_on_buyer_indicator and binding_on_buyer_indicator[0].lower() == 'true':
            lot_data = {
                "id": lot_id,
                "designContest": {
                    "bindingJuryDecision": True
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_lot_jury_decision_binding(release_json, lot_jury_decision_binding_data):
    if not lot_jury_decision_binding_data:
        logger.warning("No lot jury decision binding data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in lot_jury_decision_binding_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("designContest", {}).update(new_lot["designContest"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged lot jury decision binding data for {len(lot_jury_decision_binding_data['tender']['lots'])} lots")