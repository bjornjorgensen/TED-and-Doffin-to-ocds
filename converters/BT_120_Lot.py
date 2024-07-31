# converters/BT_120_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_no_negotiation_necessary(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"lots": []}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        no_negotiation = lot.xpath("cac:TenderingTerms/cac:AwardingTerms/cbc:NoFurtherNegotiationIndicator/text()", namespaces=namespaces)
        
        if no_negotiation:
            result["lots"].append({
                "id": lot_id,
                "secondStage": {
                    "noNegotiationNecessary": no_negotiation[0].lower() == 'true'
                }
            })

    return result if result["lots"] else None

def merge_no_negotiation_necessary(release_json, no_negotiation_data):
    if not no_negotiation_data:
        logger.warning("No No Negotiation Necessary data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in no_negotiation_data["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("secondStage", {})["noNegotiationNecessary"] = new_lot["secondStage"]["noNegotiationNecessary"]
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged No Negotiation Necessary data for {len(no_negotiation_data['lots'])} lots")