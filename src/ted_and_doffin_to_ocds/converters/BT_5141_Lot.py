# converters/BT_5141_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

# ISO 3166-1 alpha-3 to alpha-2 conversion dictionary for European countries
ISO_3166_CONVERSION = {
    "ALB": "AL",
    "AND": "AD",
    "AUT": "AT",
    "BLR": "BY",
    "BEL": "BE",
    "BIH": "BA",
    "BGR": "BG",
    "HRV": "HR",
    "CYP": "CY",
    "CZE": "CZ",
    "DNK": "DK",
    "EST": "EE",
    "FIN": "FI",
    "FRA": "FR",
    "DEU": "DE",
    "GRC": "GR",
    "HUN": "HU",
    "ISL": "IS",
    "IRL": "IE",
    "ITA": "IT",
    "KAZ": "KZ",
    "XKX": "XK",
    "LVA": "LV",
    "LIE": "LI",
    "LTU": "LT",
    "LUX": "LU",
    "MLT": "MT",
    "MDA": "MD",
    "MCO": "MC",
    "MNE": "ME",
    "NLD": "NL",
    "MKD": "MK",
    "NOR": "NO",
    "POL": "PL",
    "PRT": "PT",
    "ROU": "RO",
    "RUS": "RU",
    "SMR": "SM",
    "SRB": "RS",
    "SVK": "SK",
    "SVN": "SI",
    "ESP": "ES",
    "SWE": "SE",
    "CHE": "CH",
    "TUR": "TR",
    "UKR": "UA",
    "GBR": "GB",
    "VAT": "VA",
}


def parse_lot_country(xml_content):
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        country_codes = lot.xpath(
            ".//cac:RealizedLocation/cac:Address/cac:Country/cbc:IdentificationCode/text()",
            namespaces=namespaces,
        )

        if country_codes:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "deliveryAddresses": [
                    {"country": convert_country_code(code)} for code in country_codes
                ],
                "relatedLot": lot_id,
            }
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def convert_country_code(code):
    """
    Convert ISO 3166-1 alpha-3 country code to alpha-2 code.
    If the code is not found in the conversion dictionary, return the original code.
    """
    return ISO_3166_CONVERSION.get(code, code)


def merge_lot_country(release_json, lot_country_data):
    if not lot_country_data:
        logger.warning("No Lot Country data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in lot_country_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            for new_address in new_item["deliveryAddresses"]:
                if new_address not in existing_addresses:
                    existing_addresses.append(new_address)
        else:
            existing_items.append(new_item)

    logger.info(
        f"Merged Lot Country data for {len(lot_country_data['tender']['items'])} items",
    )
