# converters/BT_3201_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

# ISO 3166-1 alpha-2 country codes
ISO_3166_1_ALPHA_2 = {
    "AD": "Andorra", "AE": "United Arab Emirates", "AF": "Afghanistan",
    "NL": "Netherland", "NO": "Norway",
    # ... (include all country codes from the provided list)
    "ZA": "South Africa", "ZM": "Zambia", "ZW": "Zimbabwe"
}

def determine_scheme(country_code, system):
    if country_code in ISO_3166_1_ALPHA_2:
        return f"{country_code}-{system}"
    else:
        logger.warning(f"Unknown country code: {country_code}. Using default scheme.")
        return f"XX-{system}"  # Default scheme if country code is not recognized

def parse_tender_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        tender_reference = lot_tender.xpath("efac:TenderReference/cbc:ID/text()", namespaces=namespaces)
        
        if tender_id and tender_reference:
            # Extract country code from the tender reference
            # This is a placeholder. You might need to extract this information differently.
            country_code = tender_reference[0].split('-')[-1][:2].upper()
            
            scheme = determine_scheme(country_code, "TENDERNL")
            
            bid = {
                "id": tender_id[0],
                "identifiers": [{
                    "id": tender_reference[0],
                    "scheme": scheme
                }]
            }
            result["bids"]["details"].append(bid)

    return result if result["bids"]["details"] else None

def merge_tender_identifier(release_json, tender_identifier_data):
    if not tender_identifier_data:
        logger.warning("No Tender Identifier data to merge")
        return

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    
    for new_bid in tender_identifier_data["bids"]["details"]:
        existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_bid.setdefault("identifiers", []).extend(new_bid["identifiers"])
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Tender Identifier data for {len(tender_identifier_data['bids']['details'])} bids")