# converters/bt_708_part.py

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
    "HAT": "ht",
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
    "INA": "ia",
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
    "PLI": "pi",
    "PUS": "ps",
    "FAS": "fa",
    "POL": "pl",
    "POR": "pt",
    "PAN": "pa",
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
    "III": "ii",
    "YID": "yi",
    "YOR": "yo",
    "ZHA": "za",
}


def parse_part_documents_official_language(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the documents official language (BT-708) for procurement project parts from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed documents official language data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "documents": [
                    {
                        "id": "20210521/CTFD/ENG/7654-02",
                        "languages": [
                            "en"
                        ]
                    }
                ]
            }
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

    result = {"tender": {"documents": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
        namespaces=namespaces,
    )

    for part in parts:
        documents = part.xpath(
            "cac:TenderingTerms/cac:CallForTendersDocumentReference",
            namespaces=namespaces,
        )

        for doc in documents:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            languages = doc.xpath(
                "ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:OfficialLanguages/cac:Language/cbc:ID/text()",
                namespaces=namespaces,
            )

            if languages:
                document = {
                    "id": doc_id,
                    "languages": [
                        ISO_639_1_MAPPING.get(lang.upper(), lang.lower())
                        for lang in languages
                    ],
                }
                result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_part_documents_official_language(
    release_json: dict[str, Any],
    part_documents_data: dict[str, Any] | None,
) -> None:
    """Merge documents official language data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        part_documents_data: The documents official language data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not part_documents_data:
        logger.warning("No part documents official language data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in part_documents_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            existing_doc.setdefault("languages", []).extend(new_doc["languages"])
            existing_doc["languages"] = list(
                set(existing_doc["languages"]),
            )  # Remove duplicates
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged part documents official language data for %d documents",
        len(part_documents_data["tender"]["documents"]),
    )
