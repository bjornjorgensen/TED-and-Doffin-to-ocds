# converters/bt_5141_part.py

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


def parse_part_country(xml_content):
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

    result = {"tender": {"deliveryAddresses": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
        namespaces=namespaces,
    )

    for part in parts:
        country_codes = part.xpath(
            ".//cac:RealizedLocation/cac:Address/cac:Country/cbc:IdentificationCode/text()",
            namespaces=namespaces,
        )

        for code in country_codes:
            address = {"country": convert_country_code(code)}
            if address not in result["tender"]["deliveryAddresses"]:
                result["tender"]["deliveryAddresses"].append(address)

    return result if result["tender"]["deliveryAddresses"] else None


def convert_country_code(code):
    """
    Convert ISO 3166-1 alpha-3 country code to alpha-2 code.
    If the code is not found in the conversion dictionary, return the original code.
    """
    return ISO_3166_CONVERSION.get(code, code)


def merge_part_country(release_json, part_country_data):
    if not part_country_data:
        logger.warning("No part Country data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_addresses = tender.setdefault("deliveryAddresses", [])

    for new_address in part_country_data["tender"]["deliveryAddresses"]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)

    logger.info(
        "Merged part Country data for %d delivery addresses",
        len(part_country_data["tender"]["deliveryAddresses"]),
    )
