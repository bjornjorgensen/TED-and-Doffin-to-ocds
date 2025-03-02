import logging

from lxml import etree

logger = logging.getLogger(__name__)

# ISO 3166-1 alpha-3 to alpha-2 code mapping
ISO_3166_1_ALPHA_3_TO_ALPHA_2 = {
    "ABW": "AW",
    "AFG": "AF",
    "AFI": "AI",
    "AGO": "AO",
    "AIA": "AI",
    "ALA": "AX",
    "ALB": "AL",
    "AND": "AD",
    "ANT": "AN",
    "ARE": "AE",
    "ARG": "AR",
    "ARM": "AM",
    "ASM": "AS",
    "ATA": "AQ",
    "ATB": "BQ",
    "ATF": "TF",
    "ATG": "AG",
    "ATN": "NQ",
    "AUS": "AU",
    "AUT": "AT",
    "AZE": "AZ",
    "BDI": "BI",
    "BEL": "BE",
    "BEN": "BJ",
    "BES": "BQ",
    "BFA": "BF",
    "BGD": "BD",
    "BGR": "BG",
    "BHR": "BH",
    "BHS": "BS",
    "BIH": "BA",
    "BLM": "BL",
    "BLR": "BY",
    "BLZ": "BZ",
    "BMU": "BM",
    "BOL": "BO",
    "BRA": "BR",
    "BRB": "BB",
    "BRN": "BN",
    "BTN": "BT",
    "BUR": "BU",
    "BVT": "BV",
    "BWA": "BW",
    "BYS": "BY",
    "CAF": "CF",
    "CAN": "CA",
    "CCK": "CC",
    "CHE": "CH",
    "CHL": "CL",
    "CHN": "CN",
    "CIV": "CI",
    "CMR": "CM",
    "COD": "CD",
    "COG": "CG",
    "COK": "CK",
    "COL": "CO",
    "COM": "KM",
    "CPT": "CP",
    "CPV": "CV",
    "CRI": "CR",
    "CRQ": "CQ",
    "CSK": "CS",
    "CTE": "CT",
    "CUB": "CU",
    "CUW": "CW",
    "CXR": "CX",
    "CYM": "KY",
    "CYP": "CY",
    "CZE": "CZ",
    "DDR": "DD",
    "DEU": "DE",
    "DHY": "DY",
    "DJI": "DJ",
    "DMA": "DM",
    "DNK": "DK",
    "DOM": "DO",
    "DZA": "DZ",
    "ECU": "EC",
    "EGY": "EG",
    "ERI": "ER",
    "ESH": "EH",
    "ESP": "ES",
    "EST": "EE",
    "ETH": "ET",
    "EUR": "EU",
    "FIN": "FI",
    "FJI": "FJ",
    "FLK": "FK",
    "FRA": "FR",
    "FRO": "FO",
    "FSM": "FM",
    "FXX": "FX",
    "GAB": "GA",
    "GBR": "GB",
    "GEL": "GE",
    "GEO": "GE",
    "GGY": "GG",
    "GHA": "GH",
    "GIB": "GI",
    "GIN": "GN",
    "GLP": "GP",
    "GMB": "GM",
    "GNB": "GW",
    "GNQ": "GQ",
    "GRC": "GR",
    "GRD": "GD",
    "GRL": "GL",
    "GTM": "GT",
    "GUF": "GF",
    "GUM": "GU",
    "GUY": "GY",
    "HKG": "HK",
    "HMD": "HM",
    "HND": "HN",
    "HRV": "HR",
    "HTI": "HT",
    "HUN": "HU",
    "HVO": "HV",
    "IDN": "ID",
    "IMN": "IM",
    "IND": "IN",
    "IOT": "IO",
    "IRL": "IE",
    "IRN": "IR",
    "IRQ": "IQ",
    "ISL": "IS",
    "ISR": "IL",
    "ITA": "IT",
    "JAM": "JM",
    "JEY": "JE",
    "JOR": "JO",
    "JPN": "JP",
    "JTN": "JT",
    "KAZ": "KZ",
    "KEN": "KE",
    "KGZ": "KG",
    "KHM": "KH",
    "KIR": "KI",
    "KNA": "KN",
    "KOR": "KR",
    "KWT": "KW",
    "LAO": "LA",
    "LBN": "LB",
    "LBR": "LR",
    "LBY": "LY",
    "LCA": "LC",
    "LIE": "LI",
    "LKA": "LK",
    "LSO": "LS",
    "LTU": "LT",
    "LUX": "LU",
    "LVA": "LV",
    "MAC": "MO",
    "MAF": "MF",
    "MAR": "MA",
    "MCO": "MC",
    "MDA": "MD",
    "MDG": "MG",
    "MDV": "MV",
    "MEX": "MX",
    "MHL": "MH",
    "MID": "MI",
    "MKD": "MK",
    "MLI": "ML",
    "MLT": "MT",
    "MMR": "MM",
    "MNE": "ME",
    "MNG": "MN",
    "MNP": "MP",
    "MOZ": "MZ",
    "MRT": "MR",
    "MSR": "MS",
    "MTQ": "MQ",
    "MUS": "MU",
    "MWI": "MW",
    "MYS": "MY",
    "MYT": "YT",
    "NAM": "NA",
    "NCL": "NC",
    "NER": "NE",
    "NFK": "NF",
    "NGA": "NG",
    "NHB": "NH",
    "NIC": "NI",
    "NIU": "NU",
    "NLD": "NL",
    "NOR": "NO",
    "NPL": "NP",
    "NRU": "NR",
    "NTZ": "NT",
    "NZL": "NZ",
    "OMN": "OM",
    "PAK": "PK",
    "PAN": "PA",
    "PCI": "PC",
    "PCN": "PN",
    "PCZ": "PZ",
    "PER": "PE",
    "PHL": "PH",
    "PLW": "PW",
    "PNG": "PG",
    "POL": "PL",
    "PRI": "PR",
    "PRK": "KP",
    "PRT": "PT",
    "PRY": "PY",
    "PSE": "PS",
    "PUS": "PU",
    "PYF": "PF",
    "QAT": "QA",
    "REU": "RE",
    "RHO": "RH",
    "ROU": "RO",
    "RUS": "RU",
    "RWA": "RW",
    "SAU": "SA",
    "SCG": "CS",
    "SDN": "SD",
    "SEN": "SN",
    "SGP": "SG",
    "SGS": "GS",
    "SHN": "SH",
    "SJM": "SJ",
    "SKM": "SK",
    "SLB": "SB",
    "SLE": "SL",
    "SLV": "SV",
    "SMR": "SM",
    "SOM": "SO",
    "SPM": "PM",
    "SRB": "RS",
    "SSD": "SS",
    "STP": "ST",
    "SUN": "SU",
    "SUR": "SR",
    "SVK": "SK",
    "SVN": "SI",
    "SWE": "SE",
    "SWZ": "SZ",
    "SXM": "SX",
    "SYC": "SC",
    "SYR": "SY",
    "TCA": "TC",
    "TCD": "TD",
    "TGO": "TG",
    "THA": "TH",
    "TJK": "TJ",
    "TKL": "TK",
    "TKM": "TM",
    "TLS": "TL",
    "TMP": "TP",
    "TON": "TO",
    "TTO": "TT",
    "TUN": "TN",
    "TUR": "TR",
    "TUV": "TV",
    "TWN": "TW",
    "TZA": "TZ",
    "UGA": "UG",
    "UKR": "UA",
    "UMI": "UM",
    "URY": "UY",
    "USA": "US",
    "UZB": "UZ",
    "VAT": "VA",
    "VCT": "VC",
    "VDR": "VD",
    "VEN": "VE",
    "VGB": "VG",
    "VIR": "VI",
    "VNM": "VN",
    "VUT": "VU",
    "WAK": "WK",
    "WLF": "WF",
    "WSM": "WS",
    "XAC": "",
    "XAD": "",
    "XBA": "",
    "XBH": "",
    "XBI": "",
    "XCI": "",
    "XDST": "",
    "XEU": "",
    "XGS": "",
    "XHS": "",
    "XIC": "IC",
    "XIH": "",
    "XIN": "",
    "XJM": "",
    "XKA": "",
    "XKM": "",
    "XKX": "",
    "XLF": "",
    "XLI": "",
    "XLL": "",
    "XMA": "",
    "XMAZ": "",
    "XME": "",
    "XNC": "",
    "XNY": "",
    "XPA": "",
    "XPM": "",
    "XQP": "",
    "XQR": "",
    "XSC": "",
    "XSG": "",
    "XSL": "",
    "XSM": "",
    "XSV": "",
    "XWS": "",
    "XXA": "",
    "XXB": "",
    "XXC": "",
    "XXD": "",
    "XXE": "",
    "XXF": "",
    "XXG": "",
    "XXH": "",
    "XXI": "",
    "XXJ": "",
    "XXL": "",
    "XXM": "",
    "XXN": "",
    "XXO": "",
    "XXP": "",
    "XXU": "",
    "XXV": "",
    "XXZ": "",
    "YEM": "YE",
    "YMD": "YD",
    "YUG": "YU",
    "ZAF": "ZA",
    "ZAR": "ZR",
    "ZMB": "ZM",
    "ZWE": "ZW",
}


def determine_scheme(identifier: str) -> str:
    """Determine the scheme based on tender identifier format.

    Args:
        identifier: The tender reference identifier (e.g. 'BID ABD/GHI-NL/2020-002')

    Returns:
        str: Scheme in format "{country_code}-TENDERNL"

    Note:
        According to eForms guidance:
        - If the scope is subnational, set scheme to {ISO 3166-1 alpha-2}-{system}
        - Otherwise, set it to {ISO 3166-2}-{system}
        Currently defaults to using ISO 3166-1 alpha-2 format.
    """
    try:
        # Split by common delimiters
        parts = []
        for part in identifier.replace("-", "/").split("/"):
            parts.extend(part.strip().split())

        # Look for country code in parts
        for part in parts:
            clean_code = part.strip().upper()
            # Check if it's a 3-letter code
            if clean_code in ISO_3166_1_ALPHA_3_TO_ALPHA_2:
                alpha2 = ISO_3166_1_ALPHA_3_TO_ALPHA_2[clean_code]
                return f"{alpha2}-TENDERNL"
            # Check if it's already a 2-letter code
            if len(clean_code) == 2 and any(
                v == clean_code for v in ISO_3166_1_ALPHA_3_TO_ALPHA_2.values()
            ):
                return f"{clean_code}-TENDERNL"

    except Exception as e:
        logger.warning(
            "Failed to parse country code from identifier %s: %s", identifier, e
        )

    return "XX-TENDERNL"  # Default scheme if no valid country code found


def parse_tender_identifier(xml_content: str | bytes) -> dict | None:
    """Parse tender identifier information following BT-3201.

    Args:
        xml_content: XML string or bytes containing the tender notice

    Returns:
        Optional[Dict]: Dictionary containing bid identifiers, or None if no bids found
        Format: {"bids": {"details": [{"id": str, "identifiers": [{"id": str, "scheme": str}]}]}}

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

    result = {"bids": {"details": []}}

    # Only use the absolute path in the specification
    lot_tenders = root.xpath(
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        try:
            tender_id = lot_tender.xpath(
                "cbc:ID[@schemeName='tender']/text()",
                namespaces=namespaces,
            )[0]
            tender_reference = lot_tender.xpath(
                "efac:TenderReference/cbc:ID/text()",
                namespaces=namespaces,
            )[0]

            scheme = determine_scheme(tender_reference)

            bid = {
                "id": tender_id,
                "identifiers": [{"id": tender_reference, "scheme": scheme}],
            }
            result["bids"]["details"].append(bid)
        except (IndexError, AttributeError) as e:
            logger.warning("Skipping incomplete lot tender: %s", e)
            continue

    return result if result["bids"]["details"] else None


def merge_tender_identifier(release_json, tender_identifier_data) -> None:
    """Merge tender identifier data into the release JSON.

    Args:
        release_json: The target release JSON object
        tender_identifier_data: The tender identifier data to merge

    """
    if not tender_identifier_data:
        logger.warning("No Tender Identifier data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])

    for new_bid in tender_identifier_data["bids"]["details"]:
        existing_bid = next(
            (bid for bid in existing_bids if bid["id"] == new_bid["id"]),
            None,
        )
        if existing_bid:
            existing_bid.setdefault("identifiers", []).extend(new_bid["identifiers"])
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged Tender Identifier data for %d bids",
        len(tender_identifier_data["bids"]["details"]),
    )
