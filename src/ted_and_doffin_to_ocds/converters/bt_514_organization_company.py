# converters/bt_514_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# ISO 3166-1 alpha-3 to alpha-2 conversion dictionary for European countries
ISO_3166_CONVERSION = {
    "ALB": "AL",  # Albania
    "AND": "AD",  # Andorra
    "AUT": "AT",  # Austria
    "BLR": "BY",  # Belarus
    "BEL": "BE",  # Belgium
    "BIH": "BA",  # Bosnia and Herzegovina
    "BGR": "BG",  # Bulgaria
    "HRV": "HR",  # Croatia
    "CYP": "CY",  # Cyprus
    "CZE": "CZ",  # Czech Republic
    "DNK": "DK",  # Denmark
    "EST": "EE",  # Estonia
    "FIN": "FI",  # Finland
    "FRA": "FR",  # France
    "DEU": "DE",  # Germany
    "GRC": "GR",  # Greece
    "HUN": "HU",  # Hungary
    "ISL": "IS",  # Iceland
    "IRL": "IE",  # Ireland
    "ITA": "IT",  # Italy
    "KAZ": "KZ",  # Kazakhstan
    "XKX": "XK",  # Kosovo (user-assigned code)
    "LVA": "LV",  # Latvia
    "LIE": "LI",  # Liechtenstein
    "LTU": "LT",  # Lithuania
    "LUX": "LU",  # Luxembourg
    "MLT": "MT",  # Malta
    "MDA": "MD",  # Moldova
    "MCO": "MC",  # Monaco
    "MNE": "ME",  # Montenegro
    "NLD": "NL",  # Netherlands
    "MKD": "MK",  # North Macedonia
    "NOR": "NO",  # Norway
    "POL": "PL",  # Poland
    "PRT": "PT",  # Portugal
    "ROU": "RO",  # Romania
    "RUS": "RU",  # Russia
    "SMR": "SM",  # San Marino
    "SRB": "RS",  # Serbia
    "SVK": "SK",  # Slovakia
    "SVN": "SI",  # Slovenia
    "ESP": "ES",  # Spain
    "SWE": "SE",  # Sweden
    "CHE": "CH",  # Switzerland
    "TUR": "TR",  # Turkey
    "UKR": "UA",  # Ukraine
    "GBR": "GB",  # United Kingdom
    "VAT": "VA",  # Vatican City
}


def parse_organization_country(xml_content: str | bytes) -> dict | None:
    """Parse organization country information from XML content.

    Args:
        xml_content: XML string or bytes containing organization data

    Returns:
        Dict containing parsed parties data with country codes, or None if no valid data found.
        Format: {
            "parties": [
                {
                    "id": str,
                    "address": {"country": str} # ISO 3166-1 alpha-2 country code
                }
            ]
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

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:organizations/efac:organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:company/cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        country_code = organization.xpath(
            "efac:company/cac:PostalAddress/cac:Country/cbc:IdentificationCode/text()",
            namespaces=namespaces,
        )

        if org_id and country_code:
            party = {
                "id": org_id[0],
                "address": {"country": convert_country_code(country_code[0])},
            }
            result["parties"].append(party)

    return result if result["parties"] else None


def convert_country_code(code: str) -> str:
    """Convert ISO 3166-1 alpha-3 country code to alpha-2 code.

    Args:
        code: ISO 3166-1 alpha-3 country code (e.g. 'GBR')

    Returns:
        ISO 3166-1 alpha-2 country code (e.g. 'GB').
        If code not found in conversion dictionary, returns original code.
    """
    return ISO_3166_CONVERSION.get(code, code)


def merge_organization_country(
    release_json: dict, organization_country_data: dict | None
) -> None:
    """Merge organization country data into the release JSON.

    Updates existing parties' address information with country codes.
    Creates new party entries for organizations not already present in release_json.
    Country codes are converted from ISO 3166-1 alpha-3 to alpha-2 format.

    Args:
        release_json: The target release JSON to update
        organization_country_data: Dictionary containing organization country data to merge

    Returns:
        None. Updates release_json in place.
    """
    if not organization_country_data:
        logger.warning("No organization Country data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_country_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization Country data for %s parties",
        len(organization_country_data["parties"]),
    )
