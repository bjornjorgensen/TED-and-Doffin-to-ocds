# converters/bt_514_ubo.py

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


def parse_ubo_country(xml_content: str | bytes) -> dict | None:
    """Parse ultimate beneficial owner country information from XML content.

    Args:
        xml_content: XML string or bytes containing UBO data

    Returns:
        Dict containing parsed parties data with country codes, or None if no valid data found.
        Format: {
            "parties": [
                {
                    "id": str,
                    "beneficialOwners": [
                        {
                            "id": str,
                            "address": {"country": str} # ISO 3166-1 alpha-2 country code
                        }
                    ]
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
        "//efac:Organizations/efac:Organization", namespaces=namespaces
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )

        if org_id:
            party = {"id": org_id[0], "beneficialOwners": []}

            ubos = root.xpath(
                "//efac:Organizations/efac:UltimateBeneficialOwner",
                namespaces=namespaces,
            )
            for ubo in ubos:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()",
                    namespaces=namespaces,
                )
                country_code = ubo.xpath(
                    "cac:ResidenceAddress/cac:Country/cbc:IdentificationCode/text()",
                    namespaces=namespaces,
                )

                if ubo_id and country_code:
                    party["beneficialOwners"].append(
                        {
                            "id": ubo_id[0],
                            "address": {
                                "country": convert_country_code(country_code[0])
                            },
                        }
                    )

            if party["beneficialOwners"]:
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


def merge_ubo_country(release_json: dict, ubo_country_data: dict | None) -> None:
    """Merge UBO country data into the release JSON.

    Updates existing parties' beneficial owners information with country codes.
    Creates new party entries for organizations not already present in release_json.
    Country codes are converted from ISO 3166-1 alpha-3 to alpha-2 format.

    Args:
        release_json: The target release JSON to update
        ubo_country_data: Dictionary containing UBO country data to merge

    Returns:
        None. Updates release_json in place.

    """
    if not ubo_country_data:
        logger.warning("No ubo Country data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_country_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners",
                [],
            )
            for new_bo in new_party["beneficialOwners"]:
                existing_bo = next(
                    (
                        bo
                        for bo in existing_beneficial_owners
                        if bo["id"] == new_bo["id"]
                    ),
                    None,
                )
                if existing_bo:
                    existing_bo.setdefault("address", {}).update(new_bo["address"])
                else:
                    existing_beneficial_owners.append(new_bo)
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged ubo Country data for %s parties",
        len(ubo_country_data["parties"]),
    )
