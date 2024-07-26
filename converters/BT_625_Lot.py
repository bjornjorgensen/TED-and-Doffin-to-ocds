# converters/BT_625_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

EU_MEASUREMENT_UNITS = {
    "2N": "decibel", "3C": "manmonth", "AD": "byte", "AMP": "ampere", "BAR": "bar",
    "BIT": "bit", "BQL": "becquerel", "C34": "mole", "C45": "nanometre", "CDL": "candela",
    "CEL": "degree Celsius", "CMK": "square centimetre", "CMQ": "cubic centimetre",
    "CMT": "centimetre", "D30": "terajoule", "E34": "gigabyte", "GRM": "gram",
    "GTE": "gross tonnage", "GWH": "gigawatt-hour", "H87": "piece", "HAR": "hectare",
    "HLT": "hectolitre", "HTZ": "hertz", "HUR": "hour", "JOU": "joule", "KEL": "kelvin",
    "KGM": "kilogram", "KMH": "kilometre per hour", "KMK": "square kilometre",
    "KTM": "kilometre", "KWH": "kilowatt-hour", "KWT": "kilowatt", "LH": "labour hour",
    "LTR": "litre", "MAW": "megawatt", "MC": "microgram", "MGM": "milligram",
    "MIN": "minute", "MLT": "millilitre", "MMT": "millimetre", "MTK": "square metre",
    "MTR": "metre", "MTS": "metre per second", "NEW": "newton", "PAL": "pascal",
    "SEC": "second", "TKM": "tonne-kilometre", "TNE": "tonne",
    "TOE": "tonne of oil equivalent", "VLT": "volt", "WTT": "watt"
}

def parse_unit(xml_content):
    """
    Parse the XML content to extract unit information for each lot.

    This function processes the BT-625-Lot business term, which represents
    the unit which the good, service, or work comes in.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unit data in the format:
              {
                  "tender": {
                      "items": [
                          {
                              "id": "item_id",
                              "unit": {
                                  "id": "unit_code",
                                  "scheme": "EU Measurement unit",
                                  "name": "unit_name"
                              },
                              "relatedLot": "lot_id"
                          }
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
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"items": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for index, lot in enumerate(lots, start=1):
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        unit_code = lot.xpath("cac:ProcurementProject/cbc:EstimatedOverallContractQuantity/@unitCode", namespaces=namespaces)
        
        if unit_code:
            unit_code = unit_code[0]
            item_data = {
                "id": str(index),
                "unit": {
                    "id": unit_code,
                    "scheme": "EU Measurement unit",
                    "name": EU_MEASUREMENT_UNITS.get(unit_code, "Unknown")
                },
                "relatedLot": lot_id
            }
            result["tender"]["items"].append(item_data)

    return result if result["tender"]["items"] else None

def merge_unit(release_json, unit_data):
    """
    Merge the parsed unit data into the main OCDS release JSON.

    This function updates the existing items in the release JSON with the
    unit information. If an item doesn't exist, it adds a new item to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unit_data (dict): The parsed unit data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unit_data:
        logger.warning("BT-625-Lot: No unit data to merge")
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
    
    for new_item in unit_data["tender"]["items"]:
        existing_item = next((item for item in existing_items if item["id"] == new_item["id"]), None)
        if existing_item:
            existing_item["unit"] = new_item["unit"]
            existing_item["relatedLot"] = new_item["relatedLot"]
        else:
            existing_items.append(new_item)

    logger.info(f"BT-625-Lot: Merged unit data for {len(unit_data['tender']['items'])} items")