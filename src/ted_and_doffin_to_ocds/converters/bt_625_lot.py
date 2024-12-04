# converters/bt_625_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

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
    "WTT": "watt",
}


def parse_unit(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the unit (BT-625) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed unit data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "items": [
                    {
                        "id": "1",
                        "unit": {
                            "id": "TNE",
                            "scheme": "EU Measurement unit",
                            "name": "tonne"
                        },
                        "relatedLot": "LOT-0001"
                    }
                ]
            }
        }
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for index, lot in enumerate(lots, start=1):
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        unit_code = lot.xpath(
            "cac:ProcurementProject/cbc:EstimatedOverallContractQuantity/@unitCode",
            namespaces=namespaces,
        )

        if unit_code:
            unit_code = unit_code[0]
            item_data = {
                "id": str(index),
                "unit": {
                    "id": unit_code,
                    "scheme": "EU Measurement unit",
                    "name": EU_MEASUREMENT_UNITS.get(unit_code, "Unknown"),
                },
                "relatedLot": lot_id,
            }
            result["tender"]["items"].append(item_data)

    return result if result["tender"]["items"] else None


def merge_unit(
    release_json: dict[str, Any],
    unit_data: dict[str, Any] | None,
) -> None:
    """Merge unit data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        unit_data: The unit data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not unit_data:
        logger.warning("BT-625-Lot: No unit data to merge")
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in unit_data["tender"]["items"]:
        existing_item = next(
            (item for item in existing_items if item["id"] == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item["unit"] = new_item["unit"]
            existing_item["relatedLot"] = new_item["relatedLot"]
        else:
            existing_items.append(new_item)

    logger.info(
        "BT-625-Lot: Merged unit data for %d items", len(unit_data["tender"]["items"])
    )
