# converters/BT_625_Lot_Unit.py
from lxml import etree

# EU Measurement unit code to name mapping
EU_MEASUREMENT_UNITS = {
    "2N": "decibel",
    "3C": "manmonth",
    "AD": "byte",
    "AMP": "ampere",
    "BAR": "bar",
    "BIT": "bit",
    "BQL": "becquerel",
    "C34": "mole",
    "C45": "nanometre",
    "CDL": "candela",
    "CEL": "degree Celsius",
    "CMK": "square centimetre",
    "CMQ": "cubic centimetre",
    "CMT": "centimetre",
    "D30": "terajoule",
    "E34": "gigabyte",
    "GRM": "gram",
    "GTE": "gross tonnage",
    "GWH": "gigawatt-hour",
    "H87": "piece",
    "HAR": "hectare",
    "HLT": "hectolitre",
    "HTZ": "hertz",
    "HUR": "hour",
    "JOU": "joule",
    "KEL": "kelvin",
    "KGM": "kilogram",
    "KMH": "kilometre per hour",
    "KMK": "square kilometre",
    "KTM": "kilometre",
    "KWH": "kilowatt-hour",
    "KWT": "kilowatt",
    "LH": "labour hour",
    "LTR": "litre",
    "MAW": "megawatt",
    "MC": "microgram",
    "MGM": "milligram",
    "MIN": "minute",
    "MLT": "millilitre",
    "MMT": "millimetre",
    "MTK": "square metre",
    "MTR": "metre",
    "MTS": "metre per second",
    "NEW": "newton",
    "PAL": "pascal",
    "SEC": "second",
    "TKM": "tonne-kilometre",
    "TNE": "tonne",
    "TOE": "tonne of oil equivalent",
    "VLT": "volt",
    "WTT": "watt"
}

def parse_lot_unit(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        unit_code = lot.xpath("cac:ProcurementProject/cbc:EstimatedOverallContractQuantity/@unitCode", namespaces=namespaces)
        
        if unit_code:
            unit_code = unit_code[0]
            result.append({
                "relatedLot": lot_id,
                "unit": {
                    "id": unit_code,
                    "scheme": "EU Measurement unit",
                    "name": EU_MEASUREMENT_UNITS.get(unit_code, "Unknown")
                }
            })

    return result

def merge_lot_unit(release_json, unit_data):
    if unit_data:
        tender = release_json.setdefault("tender", {})
        items = tender.setdefault("items", [])

        for data in unit_data:
            existing_item = next((item for item in items if item.get("relatedLot") == data["relatedLot"]), None)
            if existing_item:
                existing_item["unit"] = data["unit"]
            else:
                new_item = {
                    "id": str(len(items) + 1),
                    "relatedLot": data["relatedLot"],
                    "unit": data["unit"]
                }
                items.append(new_item)

    return release_json