"""Converter for BT-737-Part: Document unofficial language information.

This module handles mapping of unofficial document translations from eForms to OCDS
for Part elements. It converts ISO 639-2 language codes to ISO 639-1 format.
"""

import logging

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
    "ZUL": "zu",
}

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def part_parse_documents_unofficial_language(
    xml_content: str | bytes,
) -> dict | None:
    """Parse document unofficial language translations for Part elements.

    Gets documents with unofficial translations from CallForTendersDocumentReference
    elements and converts ISO 639-2 language codes (e.g. 'ENG') to ISO 639-1 (e.g. 'en').

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "documents": [
                        {
                            "id": str,  # Document ID
                            "unofficialTranslations": [str],  # ISO 639-1 codes
                            "relatedLots": [str]  # Part ID
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"documents": []}}

        # Find all part elements first, to associate documents with their parts
        parts = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
            namespaces=NAMESPACES,
        )

        for part in parts:
            part_id = part.xpath("cbc:ID/text()", namespaces=NAMESPACES)
            if not part_id:
                continue

            part_id = part_id[0]

            # Find documents within this specific part
            documents = part.xpath(
                "cac:TenderingTerms/cac:CallForTendersDocumentReference",
                namespaces=NAMESPACES,
            )

            for document in documents:
                doc_id = document.xpath("cbc:ID/text()", namespaces=NAMESPACES)
                if not doc_id:
                    continue

                languages = document.xpath(
                    "ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension"
                    "/efac:NonOfficialLanguages/cac:Language/cbc:ID/text()",
                    namespaces=NAMESPACES,
                )

                if languages:
                    unofficial_langs = []
                    for lang in languages:
                        iso_code = ISO_639_1_MAPPING.get(lang.upper())
                        if iso_code:
                            unofficial_langs.append(iso_code)
                            logger.debug(
                                "Converted unofficial language %s to %s for document %s",
                                lang,
                                iso_code,
                                doc_id[0],
                            )
                        else:
                            logger.warning(
                                "Unknown language code: %s - using as is", lang
                            )
                            # If we can't map it, use the original code (lowercased)
                            unofficial_langs.append(lang.lower())

                    if unofficial_langs:
                        doc_data = {
                            "id": doc_id[0],
                            "unofficialTranslations": unofficial_langs,
                            "relatedLots": [part_id],
                        }
                        result["tender"]["documents"].append(doc_data)
                        logger.info(
                            "Added document %s with unofficial translations: %s",
                            doc_id[0],
                            ", ".join(unofficial_langs),
                        )

        return result if result["tender"]["documents"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing document unofficial languages")
        return None


def part_merge_documents_unofficial_language(
    release_json: dict, unofficial_langs: dict | None
) -> None:
    """Merge document unofficial language data into the OCDS release.

    Updates or adds unofficial translations for documents from Part elements.
    Handles merging of language codes while avoiding duplicates.

    Args:
        release_json: Main OCDS release to update
        unofficial_langs: Documents language data to merge, in format:
            {
                "tender": {
                    "documents": [
                        {
                            "id": str,
                            "unofficialTranslations": [str]  # ISO 639-1 codes
                        }
                    ]
                }
            }

    Note:
        Updates release_json in-place

    """
    if not unofficial_langs:
        logger.warning("No unofficial language data for documents to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in unofficial_langs["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_docs if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            translations = existing_doc.setdefault("unofficialTranslations", [])
            translations.extend(
                t for t in new_doc["unofficialTranslations"] if t not in translations
            )
        else:
            existing_docs.append(new_doc)

    logger.info(
        "Merged unofficial language data for %d documents",
        len(unofficial_langs["tender"]["documents"]),
    )
