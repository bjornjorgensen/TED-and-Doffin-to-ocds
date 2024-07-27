# converters/BT_737_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)
ISO_639_1_MAPPING = {
    'ABK': 'ab', 'AAR': 'aa', 'AFR': 'af', 'AKA': 'ak', 'SQI': 'sq', 'AMH': 'am', 'ARA': 'ar',
    'ARG': 'an', 'HYE': 'hy', 'ASM': 'as', 'AVA': 'av', 'AVE': 'ae', 'AYM': 'ay', 'AZE': 'az',
    'BAM': 'bm', 'BAK': 'ba', 'EUS': 'eu', 'BEL': 'be', 'BEN': 'bn', 'BIS': 'bi', 'BOS': 'bs',
    'BRE': 'br', 'BUL': 'bg', 'MYA': 'my', 'CAT': 'ca', 'CHA': 'ch', 'CHE': 'ce', 'NYA': 'ny',
    'ZHO': 'zh', 'CHU': 'cu', 'CHV': 'cv', 'COR': 'kw', 'COS': 'co', 'CRE': 'cr', 'HRV': 'hr',
    'CES': 'cs', 'DAN': 'da', 'DIV': 'dv', 'NLD': 'nl', 'DZO': 'dz', 'ENG': 'en', 'EPO': 'eo',
    'EST': 'et', 'EWE': 'ee', 'FAO': 'fo', 'FIJ': 'fj', 'FIN': 'fi', 'FRA': 'fr', 'FRY': 'fy',
    'FUL': 'ff', 'GLA': 'gd', 'GLG': 'gl', 'LUG': 'lg', 'KAT': 'ka', 'DEU': 'de', 'ELL': 'el',
    'KAL': 'kl', 'GRN': 'gn', 'GUJ': 'gu', 'HAT': 'ht', 'HAU': 'ha', 'HEB': 'he', 'HER': 'hz',
    'HIN': 'hi', 'HMO': 'ho', 'HUN': 'hu', 'ISL': 'is', 'IDO': 'io', 'IBO': 'ig', 'IND': 'id',
    'INA': 'ia', 'ILE': 'ie', 'IKU': 'iu', 'IPK': 'ik', 'GLE': 'ga', 'ITA': 'it', 'JPN': 'ja',
    'JAV': 'jv', 'KAN': 'kn', 'KAU': 'kr', 'KAS': 'ks', 'KAZ': 'kk', 'KHM': 'km', 'KIK': 'ki',
    'KIN': 'rw', 'KIR': 'ky', 'KOM': 'kv', 'KON': 'kg', 'KOR': 'ko', 'KUA': 'kj', 'KUR': 'ku',
    'LAO': 'lo', 'LAT': 'la', 'LAV': 'lv', 'LIM': 'li', 'LIN': 'ln', 'LIT': 'lt', 'LUB': 'lu',
    'LTZ': 'lb', 'MKD': 'mk', 'MLG': 'mg', 'MSA': 'ms', 'MAL': 'ml', 'MLT': 'mt', 'GLV': 'gv',
    'MRI': 'mi', 'MAR': 'mr', 'MAH': 'mh', 'MON': 'mn', 'NAU': 'na', 'NAV': 'nv', 'NDE': 'nd',
    'NBL': 'nr', 'NDO': 'ng', 'NEP': 'ne', 'NOR': 'no', 'NOB': 'nb', 'NNO': 'nn', 'OCI': 'oc',
    'OJI': 'oj', 'ORI': 'or', 'ORM': 'om', 'OSS': 'os', 'PLI': 'pi', 'PUS': 'ps', 'FAS': 'fa',
    'POL': 'pl', 'POR': 'pt', 'PAN': 'pa', 'QUE': 'qu', 'RON': 'ro', 'ROH': 'rm', 'RUN': 'rn',
    'RUS': 'ru', 'SME': 'se', 'SMO': 'sm', 'SAG': 'sg', 'SAN': 'sa', 'SRD': 'sc', 'SRP': 'sr',
    'SNA': 'sn', 'SND': 'sd', 'SIN': 'si', 'SLK': 'sk', 'SLV': 'sl', 'SOM': 'so', 'SOT': 'st',
    'SPA': 'es', 'SUN': 'su', 'SWA': 'sw', 'SSW': 'ss', 'SWE': 'sv', 'TGL': 'tl', 'TAH': 'ty',
    'TGK': 'tg', 'TAM': 'ta', 'TAT': 'tt', 'TEL': 'te', 'THA': 'th', 'BOD': 'bo', 'TIR': 'ti',
    'TON': 'to', 'TSO': 'ts', 'TSN': 'tn', 'TUR': 'tr', 'TUK': 'tk', 'TWI': 'tw', 'UIG': 'ug',
    'UKR': 'uk', 'URD': 'ur', 'UZB': 'uz', 'VEN': 've', 'VIE': 'vi', 'VOL': 'vo', 'WLN': 'wa',
    'CYM': 'cy', 'WOL': 'wo', 'XHO': 'xh', 'III': 'ii', 'YID': 'yi', 'YOR': 'yo', 'ZHA': 'za',
    'ZUL': 'zu'
}

def parse_documents_unofficial_language(xml_content):
    """
    Parse the XML content to extract the unofficial languages for documents in each lot.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unofficial language data for documents.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"tender": {"documents": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        documents = lot.xpath(".//cac:CallForTendersDocumentReference", namespaces=namespaces)
        
        for document in documents:
            doc_id = document.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            languages = document.xpath(".//efac:NonOfficialLanguages/cac:Language/cbc:ID/text()", namespaces=namespaces)
            
            if languages:
                doc_data = {
                    "id": doc_id,
                    "unofficialTranslations": [ISO_639_1_MAPPING.get(lang.upper(), lang.lower()) for lang in languages],
                    "relatedLots": [lot_id]
                }
                result["tender"]["documents"].append(doc_data)

    return result if result["tender"]["documents"] else None

def merge_documents_unofficial_language(release_json, unofficial_language_data):
    """
    Merge the parsed unofficial language data for documents into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unofficial_language_data (dict): The parsed unofficial language data for documents to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unofficial_language_data:
        logger.warning("No unofficial language data for documents to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in unofficial_language_data["tender"]["documents"]:
        existing_doc = next((doc for doc in existing_documents if doc["id"] == new_doc["id"]), None)
        if existing_doc:
            existing_doc.setdefault("unofficialTranslations", []).extend(new_doc["unofficialTranslations"])
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            # Remove duplicates
            existing_doc["unofficialTranslations"] = list(set(existing_doc["unofficialTranslations"]))
            existing_doc["relatedLots"] = list(set(existing_doc["relatedLots"]))
        else:
            existing_documents.append(new_doc)

    logger.info(f"Merged unofficial language data for {len(unofficial_language_data['tender']['documents'])} documents")