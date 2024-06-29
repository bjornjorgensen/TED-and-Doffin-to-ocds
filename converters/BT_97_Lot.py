# converters/BT_97_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

# ISO 639-2 to ISO 639-1 mapping (add more as needed)
LANGUAGE_MAPPING = {
    "ENG": "en",
    "FRA": "fr",
    "DEU": "de",
    "ITA": "it",
    "SPA": "es",
    # Add more mappings as needed
}

def map_language_code(iso_639_2):
    return LANGUAGE_MAPPING.get(iso_639_2, iso_639_2.lower())

def parse_submission_language(xml_content):
    logger.info("Parsing BT-97-Lot: Submission Language")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    logger.debug(f"Found {len(lot_elements)} lot elements")
    
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        language_codes = lot.xpath(
            "cac:TenderingTerms/cac:Language/cbc:ID/text()",
            namespaces=namespaces
        )
        
        if language_codes:
            mapped_languages = [map_language_code(code) for code in language_codes]
            logger.debug(f"Lot {lot_id} has Submission Languages: {mapped_languages}")
            result["tender"]["lots"].append({
                "id": lot_id,
                "submissionTerms": {
                    "languages": mapped_languages
                }
            })
        else:
            logger.debug(f"No Submission Language found for lot {lot_id}")

    logger.info(f"Parsed Submission Language for {len(result['tender']['lots'])} lots")
    return result

def merge_submission_language(release_json, submission_language_data):
    logger.info("Merging BT-97-Lot: Submission Language")
    if not submission_language_data["tender"]["lots"]:
        logger.warning("No Submission Language data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lang_lot in submission_language_data["tender"]["lots"]:
        lot_id = lang_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)
        
        if existing_lot:
            existing_submission_terms = existing_lot.setdefault("submissionTerms", {})
            existing_languages = existing_submission_terms.setdefault("languages", [])
            new_languages = lang_lot["submissionTerms"]["languages"]
            
            for lang in new_languages:
                if lang not in existing_languages:
                    existing_languages.append(lang)
            
            logger.debug(f"Updated Submission Language for existing lot {lot_id}")
        else:
            lots.append(lang_lot)
            logger.debug(f"Added new lot {lot_id} with Submission Language")

    logger.info(f"Merged Submission Language for {len(submission_language_data['tender']['lots'])} lots")