# converters/BT_191_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

# ISO 3166-1 alpha-3 to alpha-2 code mapping
ISO_3166_1_ALPHA_3_TO_ALPHA_2 = {
    "ABW": "AW", "AFG": "AF", "AFI": "AI", "AGO": "AO", "AIA": "AI", "ALA": "AX", "ALB": "AL",
    "AND": "AD", "ANT": "AN", "ARE": "AE", "ARG": "AR", "ARM": "AM", "ASM": "AS", "ATA": "AQ",
    "ATB": "BQ", "ATF": "TF", "ATG": "AG", "ATN": "NQ", "AUS": "AU", "AUT": "AT", "AZE": "AZ",
    "BDI": "BI", "BEL": "BE", "BEN": "BJ", "BES": "BQ", "BFA": "BF", "BGD": "BD", "BGR": "BG",
    "BHR": "BH", "BHS": "BS", "BIH": "BA", "BLM": "BL", "BLR": "BY", "BLZ": "BZ", "BMU": "BM",
    "BOL": "BO", "BRA": "BR", "BRB": "BB", "BRN": "BN", "BTN": "BT", "BUR": "BU", "BVT": "BV",
    "BWA": "BW", "BYS": "BY", "CAF": "CF", "CAN": "CA", "CCK": "CC", "CHE": "CH", "CHL": "CL",
    "CHN": "CN", "CIV": "CI", "CMR": "CM", "COD": "CD", "COG": "CG", "COK": "CK", "COL": "CO",
    "COM": "KM", "CPT": "CP", "CPV": "CV", "CRI": "CR", "CRQ": "CQ", "CSK": "CS", "CTE": "CT",
    "CUB": "CU", "CUW": "CW", "CXR": "CX", "CYM": "KY", "CYP": "CY", "CZE": "CZ", "DDR": "DD",
    "DEU": "DE", "DHY": "DY", "DJI": "DJ", "DMA": "DM", "DNK": "DK", "DOM": "DO", "DZA": "DZ",
    "ECU": "EC", "EGY": "EG", "ERI": "ER", "ESH": "EH", "ESP": "ES", "EST": "EE", "ETH": "ET",
    "EUR": "EU", "FIN": "FI", "FJI": "FJ", "FLK": "FK", "FRA": "FR", "FRO": "FO", "FSM": "FM",
    "FXX": "FX", "GAB": "GA", "GBR": "GB", "GEL": "GE", "GEO": "GE", "GGY": "GG", "GHA": "GH",
    "GIB": "GI", "GIN": "GN", "GLP": "GP", "GMB": "GM", "GNB": "GW", "GNQ": "GQ", "GRC": "GR",
    "GRD": "GD", "GRL": "GL", "GTM": "GT", "GUF": "GF", "GUM": "GU", "GUY": "GY", "HKG": "HK",
    "HMD": "HM", "HND": "HN", "HRV": "HR", "HTI": "HT", "HUN": "HU", "HVO": "HV", "IDN": "ID",
    "IMN": "IM", "IND": "IN", "IOT": "IO", "IRL": "IE", "IRN": "IR", "IRQ": "IQ", "ISL": "IS",
    "ISR": "IL", "ITA": "IT", "JAM": "JM", "JEY": "JE", "JOR": "JO", "JPN": "JP", "JTN": "JT",
    "KAZ": "KZ", "KEN": "KE", "KGZ": "KG", "KHM": "KH", "KIR": "KI", "KNA": "KN", "KOR": "KR",
    "KWT": "KW", "LAO": "LA", "LBN": "LB", "LBR": "LR", "LBY": "LY", "LCA": "LC", "LIE": "LI",
    "LKA": "LK", "LSO": "LS", "LTU": "LT", "LUX": "LU", "LVA": "LV", "MAC": "MO", "MAF": "MF",
    "MAR": "MA", "MCO": "MC", "MDA": "MD", "MDG": "MG", "MDV": "MV", "MEX": "MX", "MHL": "MH",
    "MID": "MI", "MKD": "MK", "MLI": "ML", "MLT": "MT", "MMR": "MM", "MNE": "ME", "MNG": "MN",
    "MNP": "MP", "MOZ": "MZ", "MRT": "MR", "MSR": "MS", "MTQ": "MQ", "MUS": "MU", "MWI": "MW",
    "MYS": "MY", "MYT": "YT", "NAM": "NA", "NCL": "NC", "NER": "NE", "NFK": "NF", "NGA": "NG",
    "NHB": "NH", "NIC": "NI", "NIU": "NU", "NLD": "NL", "NOR": "NO", "NPL": "NP", "NRU": "NR",
    "NTZ": "NT", "NZL": "NZ", "OMN": "OM", "PAK": "PK", "PAN": "PA", "PCI": "PC", "PCN": "PN",
    "PCZ": "PZ", "PER": "PE", "PHL": "PH", "PLW": "PW", "PNG": "PG", "POL": "PL", "PRI": "PR",
    "PRK": "KP", "PRT": "PT", "PRY": "PY", "PSE": "PS", "PUS": "PU", "PYF": "PF", "QAT": "QA",
    "REU": "RE", "RHO": "RH", "ROU": "RO", "RUS": "RU", "RWA": "RW", "SAU": "SA", "SCG": "CS",
    "SDN": "SD", "SEN": "SN", "SGP": "SG", "SGS": "GS", "SHN": "SH", "SJM": "SJ", "SKM": "SK",
    "SLB": "SB", "SLE": "SL", "SLV": "SV", "SMR": "SM", "SOM": "SO", "SPM": "PM", "SRB": "RS",
    "SSD": "SS", "STP": "ST", "SUN": "SU", "SUR": "SR", "SVK": "SK", "SVN": "SI", "SWE": "SE",
    "SWZ": "SZ", "SXM": "SX", "SYC": "SC", "SYR": "SY", "TCA": "TC", "TCD": "TD", "TGO": "TG",
    "THA": "TH", "TJK": "TJ", "TKL": "TK", "TKM": "TM", "TLS": "TL", "TMP": "TP", "TON": "TO",
    "TTO": "TT", "TUN": "TN", "TUR": "TR", "TUV": "TV", "TWN": "TW", "TZA": "TZ", "UGA": "UG",
    "UKR": "UA", "UMI": "UM", "URY": "UY", "USA": "US", "UZB": "UZ", "VAT": "VA", "VCT": "VC",
    "VDR": "VD", "VEN": "VE", "VGB": "VG", "VIR": "VI", "VNM": "VN", "VUT": "VU", "WAK": "WK",
    "WLF": "WF", "WSM": "WS", "XAC": "", "XAD": "", "XBA": "", "XBH": "", "XBI": "", "XCI": "",
    "XDST": "", "XEU": "", "XGS": "", "XHS": "", "XIC": "IC", "XIH": "", "XIN": "", "XJM": "",
    "XKA": "", "XKM": "", "XKX": "", "XLF": "", "XLI": "", "XLL": "", "XMA": "", "XMAZ": "",
    "XME": "", "XNC": "", "XNY": "", "XPA": "", "XPM": "", "XQP": "", "XQR": "", "XSC": "",
    "XSG": "", "XSL": "", "XSM": "", "XSV": "", "XWS": "", "XXA": "", "XXB": "", "XXC": "",
    "XXD": "", "XXE": "", "XXF": "", "XXG": "", "XXH": "", "XXI": "", "XXJ": "", "XXL": "",
    "XXM": "", "XXN": "", "XXO": "", "XXP": "", "XXU": "", "XXV": "", "XXZ": "", "YEM": "YE",
    "YMD": "YD", "YUG": "YU", "ZAF": "ZA", "ZAR": "ZR", "ZMB": "ZM", "ZWE": "ZW"
}

def parse_country_origin(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        area_code = lot_tender.xpath("efac:Origin/efbc:AreaCode[@listName='country']/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if tender_id and area_code and lot_id:
            alpha2_code = ISO_3166_1_ALPHA_3_TO_ALPHA_2.get(area_code[0], "")
            if alpha2_code:
                bid = {
                    "id": tender_id[0],
                    "countriesOfOrigin": [alpha2_code],
                    "relatedLots": [lot_id[0]]
                }
                result["bids"]["details"].append(bid)
            else:
                logger.warning(f"No matching ISO 3166-1 alpha-2 code found for {area_code[0]}")

    return result if result["bids"]["details"] else None

def merge_country_origin(release_json, country_origin_data):
    if not country_origin_data:
        logger.warning("No Country Origin data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    
    for new_bid in country_origin_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid.setdefault("countriesOfOrigin", []).extend(new_bid["countriesOfOrigin"])
            existing_bid.setdefault("relatedLots", []).extend(new_bid["relatedLots"])
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Country Origin data for {len(country_origin_data['bids']['details'])} bids")