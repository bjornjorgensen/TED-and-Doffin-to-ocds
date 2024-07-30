# converters/BT_93_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_electronic_payment(xml_content):
    """
    Parse the XML content to extract the electronic payment information for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed electronic payment data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "contractTerms": {
                                  "hasElectronicPayment": bool
                              }
                          }
                      ]
                  }
              }
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
        
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        electronic_payment = lot.xpath("cac:TenderingTerms/cac:PostAwardProcess/cbc:ElectronicPaymentUsageIndicator/text()", namespaces=namespaces)
        
        if lot_id and electronic_payment:
            lot_data = {
                "id": lot_id[0],
                "contractTerms": {
                    "hasElectronicPayment": electronic_payment[0].lower() == 'true'
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_electronic_payment(release_json, electronic_payment_data):
    """
    Merge the parsed electronic payment data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        electronic_payment_data (dict): The parsed electronic payment data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not electronic_payment_data:
        logger.warning("No electronic payment data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in electronic_payment_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(new_lot["contractTerms"])
        else:
            lots.append(new_lot)

    logger.info(f"Merged electronic payment data for {len(electronic_payment_data['tender']['lots'])} lots")