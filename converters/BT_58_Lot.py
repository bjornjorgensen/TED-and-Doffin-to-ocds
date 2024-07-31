# converters/BT_58_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_renewal_maximum(xml_content):
    """
    Parse the XML content to extract the maximum number of renewals for each lot.

    This function processes the BT-58-Lot business term, which represents the maximum
    number of times the contract can be renewed for a specific lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed renewal maximum data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "renewal": {
                                  "maximumRenewals": int
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
        maximum_renewals = lot.xpath("cac:ProcurementProject/cac:ContractExtension/cbc:MaximumNumberNumeric/text()", namespaces=namespaces)

        if lot_id and maximum_renewals:
            lot_data = {
                "id": lot_id[0],
                "renewal": {
                    "maximumRenewals": int(maximum_renewals[0])
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_renewal_maximum(release_json, renewal_data):
    """
    Merge the parsed renewal maximum data into the main OCDS release JSON.

    This function updates the existing lots in the release JSON with the renewal
    maximum information. If a lot doesn't exist, it adds a new lot to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        renewal_data (dict): The parsed renewal maximum data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not renewal_data:
        logger.warning("BT-58-Lot: No renewal maximum data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in renewal_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("renewal", {}).update(new_lot["renewal"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"BT-58-Lot: Merged renewal maximum data for {len(renewal_data['tender']['lots'])} lots")