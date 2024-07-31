# converters/BT_52_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_successive_reduction_indicator(xml_content):
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
        successive_reduction = lot.xpath("cac:TenderingProcess/cbc:CandidateReductionConstraintIndicator/text()", namespaces=namespaces)
        
        if successive_reduction:
            lot_data = {
                "id": lot_id,
                "secondStage": {
                    "successiveReduction": successive_reduction[0].lower() == 'true'
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_successive_reduction_indicator(release_json, successive_reduction_data):
    if not successive_reduction_data:
        logger.warning("No Successive Reduction Indicator data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in successive_reduction_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("secondStage", {}).update(new_lot["secondStage"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Successive Reduction Indicator data for {len(successive_reduction_data['tender']['lots'])} lots")