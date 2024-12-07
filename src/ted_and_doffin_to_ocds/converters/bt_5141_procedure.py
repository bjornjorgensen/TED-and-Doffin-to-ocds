# converters/bt_5141_procedure.py

import logging
from typing import Any

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

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_procedure_country(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse place performance country code (BT-5141) from XML content.

    Gets country code information from procedure delivery address. Creates/updates
    corresponding Address objects in tender.deliveryAddresses array.
    Converts ISO 3166-1 alpha-3 codes to alpha-2.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing tender with delivery addresses or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"deliveryAddresses": []}}

        country_codes = root.xpath(
            "//cac:ProcurementProject/cac:RealizedLocation/cac:Address/cac:Country/cbc:IdentificationCode/text()",
            namespaces=NAMESPACES,
        )

        for code in country_codes:
            if code.strip():
                converted_code = convert_country_code(code.strip())
                if converted_code:
                    address = {"country": converted_code}
                    if address not in result["tender"]["deliveryAddresses"]:
                        result["tender"]["deliveryAddresses"].append(address)

        if result["tender"]["deliveryAddresses"]:
            return result

    except Exception:
        logger.exception("Error parsing procedure country codes")
        return None

    return None


def convert_country_code(code: str) -> str:
    """
    Convert ISO 3166-1 alpha-3 country code to alpha-2 code.

    Args:
        code: ISO 3166-1 alpha-3 country code

    Returns:
        Corresponding alpha-2 code or original code if not found in conversion table
    """
    converted = ISO_3166_CONVERSION.get(code.upper())
    if not converted:
        logger.warning("No conversion found for country code: %s", code)
        return code
    return converted


def merge_procedure_country(
    release_json: dict[str, Any], procedure_country_data: dict[str, Any] | None
) -> None:
    """
    Merge country code data into the release JSON.

    Updates or creates delivery addresses with country information.
    Preserves existing address data while adding/updating country codes.

    Args:
        release_json: The target release JSON to update
        procedure_country_data: The source data containing country codes to merge

    Returns:
        None
    """
    if not procedure_country_data:
        logger.warning("No procedure Country data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_addresses = tender.setdefault("deliveryAddresses", [])

    for new_address in procedure_country_data["tender"]["deliveryAddresses"]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)

    logger.info(
        "Merged procedure Country data for %d delivery addresses",
        len(procedure_country_data["tender"]["deliveryAddresses"]),
    )
