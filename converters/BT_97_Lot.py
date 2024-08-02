# converters/BT_97_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

# ISO 639-1 language code mapping
ISO_639_1_MAPPING = {
    "AAR": "aa",  # Afar
    "ABK": "ab",  # Abkhazian
    "AFR": "af",  # Afrikaans
    "AKA": "ak",  # Akan
    "ALB": "sq",  # Albanian
    "AMH": "am",  # Amharic
    "ARA": "ar",  # Arabic
    "ARG": "an",  # Aragonese
    "ARM": "hy",  # Armenian
    "ASM": "as",  # Assamese
    "AVA": "av",  # Avaric
    "AVE": "ae",  # Avestan
    "AYM": "ay",  # Aymara
    "AZE": "az",  # Azerbaijani
    "BAK": "ba",  # Bashkir
    "BAM": "bm",  # Bambara
    "BAQ": "eu",  # Basque
    "BEL": "be",  # Belarusian
    "BEN": "bn",  # Bengali
    "BIH": "bh",  # Bihari languages
    "BIS": "bi",  # Bislama
    "BOD": "bo",  # Tibetan
    "BOS": "bs",  # Bosnian
    "BRE": "br",  # Breton
    "BUL": "bg",  # Bulgarian
    "BUR": "my",  # Burmese
    "CAT": "ca",  # Catalan; Valencian
    "CES": "cs",  # Czech
    "CHA": "ch",  # Chamorro
    "CHE": "ce",  # Chechen
    "CHI": "zh",  # Chinese
    "CHV": "cv",  # Chuvash
    "COR": "kw",  # Cornish
    "COS": "co",  # Corsican
    "CRE": "cr",  # Cree
    "CYM": "cy",  # Welsh
    "DAN": "da",  # Danish
    "DEU": "de",  # German
    "DIV": "dv",  # Divehi; Dhivehi; Maldivian
    "DZO": "dz",  # Dzongkha
    "ELL": "el",  # Greek, Modern (1453-)
    "ENG": "en",  # English
    "EPO": "eo",  # Esperanto
    "EST": "et",  # Estonian
    "EUS": "eu",  # Basque
    "EWE": "ee",  # Ewe
    "FAO": "fo",  # Faroese
    "FAS": "fa",  # Persian
    "FIJ": "fj",  # Fijian
    "FIN": "fi",  # Finnish
    "FRA": "fr",  # French
    "FRY": "fy",  # Western Frisian
    "FUL": "ff",  # Fulah
    "GAA": "ga",  # Ga
    "GLA": "gd",  # Gaelic; Scottish Gaelic
    "GLE": "ga",  # Irish
    "GLG": "gl",  # Galician
    "GLV": "gv",  # Manx
    "GRN": "gn",  # Guarani
    "GUJ": "gu",  # Gujarati
    "HAT": "ht",  # Haitian; Haitian Creole
    "HAU": "ha",  # Hausa
    "HEB": "he",  # Hebrew
    "HER": "hz",  # Herero
    "HIN": "hi",  # Hindi
    "HMO": "ho",  # Hiri Motu
    "HRV": "hr",  # Croatian
    "HUN": "hu",  # Hungarian
    "IBO": "ig",  # Igbo
    "ICE": "is",  # Icelandic
    "IDO": "io",  # Ido
    "III": "ii",  # Sichuan Yi; Nuosu
    "IKU": "iu",  # Inuktitut
    "ILE": "ie",  # Interlingue; Occidental
    "INA": "ia",  # Interlingua (International Auxiliary Language Association)
    "IND": "id",  # Indonesian
    "IPK": "ik",  # Inupiaq
    "ITA": "it",  # Italian
    "JAV": "jv",  # Javanese
    "JPN": "ja",  # Japanese
    "KAL": "kl",  # Kalaallisut; Greenlandic
    "KAN": "kn",  # Kannada
    "KAS": "ks",  # Kashmiri
    "KAU": "kr",  # Kanuri
    "KAZ": "kk",  # Kazakh
    "KHM": "km",  # Central Khmer
    "KIK": "ki",  # Kikuyu; Gikuyu
    "KIN": "rw",  # Kinyarwanda
    "KIR": "ky",  # Kirghiz; Kyrgyz
    "KOM": "kv",  # Komi
    "KON": "kg",  # Kongo
    "KOR": "ko",  # Korean
    "KUA": "kj",  # Kuanyama; Kwanyama
    "KUR": "ku",  # Kurdish
    "LAO": "lo",  # Lao
    "LAT": "la",  # Latin
    "LAV": "lv",  # Latvian
    "LIM": "li",  # Limburgan; Limburger; Limburgish
    "LIN": "ln",  # Lingala
    "LIT": "lt",  # Lithuanian
    "LTZ": "lb",  # Luxembourgish; Letzeburgesch
    "LUB": "lu",  # Luba-Katanga
    "LUG": "lg",  # Ganda
    "MAC": "mk",  # Macedonian
    "MAH": "mh",  # Marshallese
    "MAL": "ml",  # Malayalam
    "MAO": "mi",  # Maori
    "MAR": "mr",  # Marathi
    "MAY": "ms",  # Malay
    "MLG": "mg",  # Malagasy
    "MLT": "mt",  # Maltese
    "MON": "mn",  # Mongolian
    "NAU": "na",  # Nauru
    "NAV": "nv",  # Navajo; Navaho
    "NBL": "nr",  # Ndebele, South; South Ndebele
    "NDE": "nd",  # Ndebele, North; North Ndebele
    "NDO": "ng",  # Ndonga
    "NEP": "ne",  # Nepali
    "NNO": "nn",  # Norwegian Nynorsk; Nynorsk, Norwegian
    "NOB": "nb",  # Bokmål, Norwegian; Norwegian Bokmål
    "NOR": "no",  # Norwegian
    "NYA": "ny",  # Chichewa; Chewa; Nyanja
    "OCI": "oc",  # Occitan (post 1500)
    "OJI": "oj",  # Ojibwa
    "ORI": "or",  # Oriya
    "ORM": "om",  # Oromo
    "OSS": "os",  # Ossetian; Ossetic
    "PAN": "pa",  # Panjabi; Punjabi
    "PER": "fa",  # Persian
    "PLI": "pi",  # Pali
    "POL": "pl",  # Polish
    "POR": "pt",  # Portuguese
    "PUS": "ps",  # Pushto; Pashto
    "QUE": "qu",  # Quechua
    "ROH": "rm",  # Romansh
    "RON": "ro",  # Romanian; Moldavian; Moldovan
    "RUM": "ro",  # Romanian; Moldavian; Moldovan
    "RUN": "rn",  # Rundi
    "RUS": "ru",  # Russian
    "SAG": "sg",  # Sango
    "SAN": "sa",  # Sanskrit
    "SIN": "si",  # Sinhala; Sinhalese
    "SLK": "sk",  # Slovak
    "SLO": "sk",  # Slovak
    "SLV": "sl",  # Slovenian
    "SME": "se",  # Northern Sami
    "SMO": "sm",  # Samoan
    "SNA": "sn",  # Shona
    "SND": "sd",  # Sindhi
    "SOM": "so",  # Somali
    "SOT": "st",  # Sotho, Southern
    "SPA": "es",  # Spanish; Castilian
    "SQI": "sq",  # Albanian
    "SRD": "sc",  # Sardinian
    "SRP": "sr",  # Serbian
    "SSW": "ss",  # Swati
    "SUN": "su",  # Sundanese
    "SWA": "sw",  # Swahili
    "SWE": "sv",  # Swedish
    "TAH": "ty",  # Tahitian
    "TAM": "ta",  # Tamil
    "TAT": "tt",  # Tatar
    "TEL": "te",  # Telugu
    "TGK": "tg",  # Tajik
    "TGL": "tl",  # Tagalog
    "THA": "th",  # Thai
    "TIB": "bo",  # Tibetan
    "TIR": "ti",  # Tigrinya
    "TON": "to",  # Tonga (Tonga Islands)
    "TSN": "tn",  # Tswana
    "TSO": "ts",  # Tsonga
    "TUK": "tk",  # Turkmen
    "TUR": "tr",  # Turkish
    "TWI": "tw",  # Twi
    "UIG": "ug",  # Uighur; Uyghur
    "UKR": "uk",  # Ukrainian
    "URD": "ur",  # Urdu
    "UZB": "uz",  # Uzbek
    "VEN": "ve",  # Venda
    "VIE": "vi",  # Vietnamese
    "VOL": "vo",  # Volapük
    "WEL": "cy",  # Welsh
    "WLN": "wa",  # Walloon
    "WOL": "wo",  # Wolof
    "XHO": "xh",  # Xhosa
    "YID": "yi",  # Yiddish
    "YOR": "yo",  # Yoruba
    "ZHA": "za",  # Zhuang; Chuang
    "ZHO": "zh",  # Chinese
    "ZUL": "zu",  # Zulu
}

def parse_submission_language(xml_content):
    """
    Parse the XML content to extract the submission language for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed submission language data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "submissionTerms": {
                                  "languages": ["language_code", ...]
                              }
                          }
                      ]
                  }
              }
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
        
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        languages = lot.xpath("cac:TenderingTerms/cac:Language/cbc:ID/text()", namespaces=namespaces)
        
        if lot_id and languages:
            mapped_languages = [ISO_639_1_MAPPING.get(lang.upper(), lang.lower()) for lang in languages]
            lot_data = {
                "id": lot_id[0],
                "submissionTerms": {
                    "languages": mapped_languages
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_submission_language(release_json, submission_language_data):
    """
    Merge the parsed submission language data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        submission_language_data (dict): The parsed submission language data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not submission_language_data:
        logger.warning("No submission language data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in submission_language_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(new_lot["submissionTerms"])
        else:
            lots.append(new_lot)

    logger.info(f"Merged submission language data for {len(submission_language_data['tender']['lots'])} lots")