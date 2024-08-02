# converters/BT_57_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_renewal_description(xml_content):
    """
    Parse the XML content to extract renewal description information for each lot.

    This function processes the BT-57-Lot business term, which represents any other
    information about the renewal(s) for a specific lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed renewal description data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "renewal": {
                                  "description": "renewal description"
                              }
                          },
                          ...
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
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
        renewal_description = lot.xpath("cac:ProcurementProject/cac:ContractExtension/cac:Renewal/cac:Period/cbc:Description/text()", namespaces=namespaces)

        if lot_id and renewal_description:
            lot_data = {
                "id": lot_id[0],
                "renewal": {
                    "description": renewal_description[0]
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_renewal_description(release_json, renewal_data):
    """
    Merge the parsed renewal description data into the main OCDS release JSON.

    This function updates the existing lots in the release JSON with the renewal
    description information. If a lot doesn't exist, it adds a new lot to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        renewal_data (dict): The parsed renewal description data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not renewal_data:
        logger.warning("BT-57-Lot: No renewal description data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in renewal_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("renewal", {}).update(new_lot["renewal"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"BT-57-Lot: Merged renewal description data for {len(renewal_data['tender']['lots'])} lots")