# converters/BT_95_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_recurrence_description(xml_content):
    """
    Parse the XML content to extract the recurrence description for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed recurrence description data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "recurrence": {
                                  "description": "description_text"
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
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        recurrence_description = lot.xpath("cac:TenderingTerms/cbc:RecurringProcurementDescription/text()", namespaces=namespaces)
        
        if lot_id and recurrence_description:
            lot_data = {
                "id": lot_id[0],
                "recurrence": {
                    "description": recurrence_description[0]
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_recurrence_description(release_json, recurrence_description_data):
    """
    Merge the parsed recurrence description data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        recurrence_description_data (dict): The parsed recurrence description data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not recurrence_description_data:
        logger.warning("No recurrence description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in recurrence_description_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("recurrence", {}).update(new_lot["recurrence"])
        else:
            lots.append(new_lot)

    logger.info(f"Merged recurrence description data for {len(recurrence_description_data['tender']['lots'])} lots")