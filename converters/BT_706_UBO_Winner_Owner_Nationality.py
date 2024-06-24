# converters/BT_706_UBO_Winner_Owner_Nationality.py
from lxml import etree

ISO_3166_1_MAPPING = {
    'ABW': 'AW', 'AFG': 'AF', 'AFI': 'AI', 'AGO': 'AO', 'AIA': 'AI', 'ALA': 'AX', 'ALB': 'AL',
    'AND': 'AD', 'ANT': 'AN', 'ARE': 'AE', 'ARG': 'AR', 'ARM': 'AM', 'ASM': 'AS', 'ATA': 'AQ',
    'ATB': 'BQ', 'ATF': 'TF', 'ATG': 'AG', 'ATN': 'NQ', 'AUS': 'AU', 'AUT': 'AT', 'AZE': 'AZ',
    'BDI': 'BI', 'BEL': 'BE', 'BEN': 'BJ', 'BES': 'BQ', 'BFA': 'BF', 'BGD': 'BD', 'BGR': 'BG',
    'BHR': 'BH', 'BHS': 'BS', 'BIH': 'BA', 'BLM': 'BL', 'BLR': 'BY', 'BLZ': 'BZ', 'BMU': 'BM',
    'BOL': 'BO', 'BRA': 'BR', 'BRB': 'BB', 'BRN': 'BN', 'BTN': 'BT', 'BUR': 'BU', 'BVT': 'BV',
    'BWA': 'BW', 'BYS': 'BY', 'CAF': 'CF', 'CAN': 'CA', 'CCK': 'CC', 'CHE': 'CH', 'CHL': 'CL',
    'CHN': 'CN', 'CIV': 'CI', 'CMR': 'CM', 'COD': 'CD', 'COG': 'CG', 'COK': 'CK', 'COL': 'CO',
    'COM': 'KM', 'CPT': 'CP', 'CPV': 'CV', 'CRI': 'CR', 'CRQ': 'CQ', 'CSK': 'CS', 'CTE': 'CT',
    'CUB': 'CU', 'CUW': 'CW', 'CXR': 'CX', 'CYM': 'KY', 'CYP': 'CY', 'CZE': 'CZ', 'DDR': 'DD',
    'DEU': 'DE', 'DHY': 'DY', 'DJI': 'DJ', 'DMA': 'DM', 'DNK': 'DK', 'DOM': 'DO', 'DZA': 'DZ',
    'ECU': 'EC', 'EGY': 'EG', 'ERI': 'ER', 'ESH': 'EH', 'ESP': 'ES', 'EST': 'EE', 'ETH': 'ET',
    'EUR': 'EU', 'FIN': 'FI', 'FJI': 'FJ', 'FLK': 'FK', 'FRA': 'FR', 'FRO': 'FO', 'FSM': 'FM',
    'FXX': 'FX', 'GAB': 'GA', 'GBR': 'GB', 'GEL': 'GE', 'GEO': 'GE', 'GGY': 'GG', 'GHA': 'GH',
    'GIB': 'GI', 'GIN': 'GN', 'GLP': 'GP', 'GMB': 'GM', 'GNB': 'GW', 'GNQ': 'GQ', 'GRC': 'GR',
    'GRD': 'GD', 'GRL': 'GL', 'GTM': 'GT', 'GUF': 'GF', 'GUM': 'GU', 'GUY': 'GY', 'HKG': 'HK',
    'HMD': 'HM', 'HND': 'HN', 'HRV': 'HR', 'HTI': 'HT', 'HUN': 'HU', 'HVO': 'HV', 'IDN': 'ID',
    'IMN': 'IM', 'IND': 'IN', 'IOT': 'IO', 'IRL': 'IE', 'IRN': 'IR', 'IRQ': 'IQ', 'ISL': 'IS',
    'ISR': 'IL', 'ITA': 'IT', 'JAM': 'JM', 'JEY': 'JE', 'JOR': 'JO', 'JPN': 'JP', 'JTN': 'JT',
    'KAZ': 'KZ', 'KEN': 'KE', 'KGZ': 'KG', 'KHM': 'KH', 'KIR': 'KI', 'KNA': 'KN', 'KOR': 'KR',
    'KWT': 'KW', 'LAO': 'LA', 'LBN': 'LB', 'LBR': 'LR', 'LBY': 'LY', 'LCA': 'LC', 'LIE': 'LI',
    'LKA': 'LK', 'LSO': 'LS', 'LTU': 'LT', 'LUX': 'LU', 'LVA': 'LV', 'MAC': 'MO', 'MAF': 'MF',
    'MAR': 'MA', 'MCO': 'MC', 'MDA': 'MD', 'MDG': 'MG', 'MDV': 'MV', 'MEX': 'MX', 'MHL': 'MH',
    'MID': 'MI', 'MKD': 'MK', 'MLI': 'ML', 'MLT': 'MT', 'MMR': 'MM', 'MNE': 'ME', 'MNG': 'MN',
    'MNP': 'MP', 'MOZ': 'MZ', 'MRT': 'MR', 'MSR': 'MS', 'MTQ': 'MQ', 'MUS': 'MU', 'MWI': 'MW',
    'MYS': 'MY', 'MYT': 'YT', 'NAM': 'NA', 'NCL': 'NC', 'NER': 'NE', 'NFK': 'NF', 'NGA': 'NG',
    'NHB': 'NH', 'NIC': 'NI', 'NIU': 'NU', 'NLD': 'NL', 'NOR': 'NO', 'NPL': 'NP', 'NRU': 'NR',
    'NTZ': 'NT', 'NZL': 'NZ', 'OMN': 'OM', 'PAK': 'PK', 'PAN': 'PA', 'PCI': 'PC', 'PCN': 'PN',
    'PCZ': 'PZ', 'PER': 'PE', 'PHL': 'PH', 'PLW': 'PW', 'PNG': 'PG', 'POL': 'PL', 'PRI': 'PR',
    'PRK': 'KP', 'PRT': 'PT', 'PRY': 'PY', 'PSE': 'PS', 'PUS': 'PU', 'PYF': 'PF', 'QAT': 'QA',
    'REU': 'RE', 'RHO': 'RH', 'ROU': 'RO', 'RUS': 'RU', 'RWA': 'RW', 'SAU': 'SA', 'SCG': 'CS',
    'SDN': 'SD', 'SEN': 'SN', 'SGP': 'SG', 'SGS': 'GS', 'SHN': 'SH', 'SJM': 'SJ', 'SKM': 'SK',
    'SLB': 'SB', 'SLE': 'SL', 'SLV': 'SV', 'SMR': 'SM', 'SOM': 'SO', 'SPM': 'PM', 'SRB': 'RS',
    'SSD': 'SS', 'STP': 'ST', 'SUN': 'SU', 'SUR': 'SR', 'SVK': 'SK', 'SVN': 'SI', 'SWE': 'SE',
    'SWZ': 'SZ', 'SXM': 'SX', 'SYC': 'SC', 'SYR': 'SY', 'TCA': 'TC', 'TCD': 'TD', 'TGO': 'TG',
    'THA': 'TH', 'TJK': 'TJ', 'TKL': 'TK', 'TKM': 'TM', 'TLS': 'TL', 'TMP': 'TP', 'TON': 'TO',
    'TTO': 'TT', 'TUN': 'TN', 'TUR': 'TR', 'TUV': 'TV', 'TWN': 'TW', 'TZA': 'TZ', 'UGA': 'UG',
    'UKR': 'UA', 'UMI': 'UM', 'URY': 'UY', 'USA': 'US', 'UZB': 'UZ', 'VAT': 'VA', 'VCT': 'VC',
    'VDR': 'VD', 'VEN': 'VE', 'VGB': 'VG', 'VIR': 'VI', 'VNM': 'VN', 'VUT': 'VU', 'WAK': 'WK',
    'WLF': 'WF', 'WSM': 'WS', 'XIC': 'IC', 'YEM': 'YE', 'YMD': 'YD', 'YUG': 'YU', 'ZAF': 'ZA',
    'ZAR': 'ZR', 'ZMB': 'ZM', 'ZWE': 'ZW'
}

def parse_winner_owner_nationality(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = []

    ubos = root.xpath("//efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubos:
        ubo_id = ubo.xpath("cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)
        nationality = ubo.xpath("efac:Nationality/cbc:NationalityID/text()", namespaces=namespaces)
        if ubo_id and nationality:
            result.append({
                "ubo_id": ubo_id[0],
                "nationality": ISO_3166_1_MAPPING.get(nationality[0], nationality[0])
            })

    return result

def merge_winner_owner_nationality(release_json, nationality_data):
    if nationality_data:
        for party in release_json.get("parties", []):
            if "beneficialOwners" in party:
                for bo in party["beneficialOwners"]:
                    matching_data = next((data for data in nationality_data if data["ubo_id"] == bo["id"]), None)
                    if matching_data:
                        bo["nationality"] = matching_data["nationality"]

    return release_json