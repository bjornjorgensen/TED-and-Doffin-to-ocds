# converters/bt_702a_notice.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

ISO_639_1_MAPPING = {
    "ABK": "ab",
    "AAR": "aa",
    "AFR": "af",
    "AKA": "ak",
    "SQI": "sq",
    "AMH": "am",
    "ARA": "ar",
    "ARG": "an",
    "HYE": "hy",
    "ASM": "as",
    "AVA": "av",
    "AVE": "ae",
    "AYM": "ay",
    "AZE": "az",
    "BAM": "bm",
    "BAK": "ba",
    "EUS": "eu",
    "BEL": "be",
    "BEN": "bn",
    "BIS": "bi",
    "BOS": "bs",
    "BRE": "br",
    "BUL": "bg",
    "MYA": "my",
    "CAT": "ca",
    "CHA": "ch",
    "CHE": "ce",
    "NYA": "ny",
    "ZHO": "zh",
    "CHU": "cu",
    "CHV": "cv",
    "COR": "kw",
    "COS": "co",
    "CRE": "cr",
    "HRV": "hr",
    "CES": "cs",
    "DAN": "da",
    "DIV": "dv",
    "NLD": "nl",
    "DZO": "dz",
    "ENG": "en",
    "EPO": "eo",
    "EST": "et",
    "EWE": "ee",
    "FAO": "fo",
    "FIJ": "fj",
    "FIN": "fi",
    "FRA": "fr",
    "FRY": "fy",
    "FUL": "ff",
    "GLA": "gd",
    "GLG": "gl",
    "LUG": "lg",
    "KAT": "ka",
    "DEU": "de",
    "ELL": "el",
    "KAL": "kl",
    "GRN": "gn",
    "GUJ": "gu",
    "HAU": "ha",
    "HEB": "he",
    "HER": "hz",
    "HIN": "hi",
    "HMO": "ho",
    "HUN": "hu",
    "ISL": "is",
    "IDO": "io",
    "IBO": "ig",
    "IND": "id",
    "ILE": "ie",
    "IKU": "iu",
    "IPK": "ik",
    "GLE": "ga",
    "ITA": "it",
    "JPN": "ja",
    "JAV": "jv",
    "KAN": "kn",
    "KAU": "kr",
    "KAS": "ks",
    "KAZ": "kk",
    "KHM": "km",
    "KIK": "ki",
    "KIN": "rw",
    "KIR": "ky",
    "KOM": "kv",
    "KON": "kg",
    "KOR": "ko",
    "KUA": "kj",
    "KUR": "ku",
    "LAO": "lo",
    "LAT": "la",
    "LAV": "lv",
    "LIM": "li",
    "LIN": "ln",
    "LIT": "lt",
    "LUB": "lu",
    "LTZ": "lb",
    "MKD": "mk",
    "MLG": "mg",
    "MSA": "ms",
    "MAL": "ml",
    "MLT": "mt",
    "GLV": "gv",
    "MRI": "mi",
    "MAR": "mr",
    "MAH": "mh",
    "MON": "mn",
    "NAU": "na",
    "NAV": "nv",
    "NDE": "nd",
    "NBL": "nr",
    "NDO": "ng",
    "NEP": "ne",
    "NOR": "no",
    "NOB": "nb",
    "NNO": "nn",
    "OCI": "oc",
    "OJI": "oj",
    "ORI": "or",
    "ORM": "om",
    "OSS": "os",
    "PAN": "pa",
    "FAS": "fa",
    "POL": "pl",
    "POR": "pt",
    "PUS": "ps",
    "QUE": "qu",
    "RON": "ro",
    "ROH": "rm",
    "RUN": "rn",
    "RUS": "ru",
    "SME": "se",
    "SMO": "sm",
    "SAG": "sg",
    "SAN": "sa",
    "SRD": "sc",
    "SRP": "sr",
    "SNA": "sn",
    "SND": "sd",
    "SIN": "si",
    "SLK": "sk",
    "SLV": "sl",
    "SOM": "so",
    "SOT": "st",
    "SPA": "es",
    "SUN": "su",
    "SWA": "sw",
    "SSW": "ss",
    "SWE": "sv",
    "TGL": "tl",
    "TAH": "ty",
    "TGK": "tg",
    "TAM": "ta",
    "TAT": "tt",
    "TEL": "te",
    "THA": "th",
    "BOD": "bo",
    "TIR": "ti",
    "TON": "to",
    "TSO": "ts",
    "TSN": "tn",
    "TUR": "tr",
    "TUK": "tk",
    "TWI": "tw",
    "UIG": "ug",
    "UKR": "uk",
    "URD": "ur",
    "UZB": "uz",
    "VEN": "ve",
    "VIE": "vi",
    "VOL": "vo",
    "WLN": "wa",
    "CYM": "cy",
    "WOL": "wo",
    "XHO": "xh",
    "YID": "yi",
    "YOR": "yo",
    "ZHA": "za",
    "ZUL": "zu",
}


def parse_notice_language(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the notice language (BT-702) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed notice language in OCDS format, or None if no data found.
        Format:
        {
            "language": "en"
        }

    Note:
        Only the primary notice language (BT-702(a)) is included in the output.
        Additional languages (BT-702(b)) are discarded as per eForms guidance.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }

    # Primary language (BT-702(a))
    notice_language_code = root.xpath(
        "/*/cbc:NoticeLanguageCode/text()",
        namespaces=namespaces,
    )

    # We extract but discard additional languages as per eForms guidance
    # additional_languages = root.xpath(
    #     "/*/cac:AdditionalNoticeLanguage/cbc:ID/text()",
    #     namespaces=namespaces,
    # )

    if notice_language_code:
        iso_639_1_code = ISO_639_1_MAPPING.get(notice_language_code[0].upper())
        if iso_639_1_code:
            return {"language": iso_639_1_code}

    return None


def merge_notice_language(
    release_json: dict[str, Any],
    notice_language_data: dict[str, Any] | None,
) -> None:
    """Merge notice language data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        notice_language_data: The notice language data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not notice_language_data:
        logger.warning("No notice Language data to merge")
        return

    release_json.update(notice_language_data)
    logger.info("Merged notice Language data: %s", notice_language_data["language"])
