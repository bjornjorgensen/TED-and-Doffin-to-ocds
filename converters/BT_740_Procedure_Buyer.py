# converters/BT_740_Procedure_Buyer.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

buyer_contracting_type_mapping = {
    'cont-ent': 'Contracting Entity',
    'not-cont-ent': 'Not Contracting Entity'
}

def parse_buyer_contracting_entity(xml_content):
    """
    Parse the XML content to extract the buyer contracting entity information.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed buyer contracting entity data.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes
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

    result = {"parties": []}

    xpath_query = "//cac:ContractingPartyType"
    contracting_party_types = root.xpath(xpath_query, namespaces=namespaces)
    
    for cpt in contracting_party_types:
        org_id = cpt.xpath("cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        party_type_code = cpt.xpath("cbc:PartyTypeCode[@listName='buyer-contracting-type']/text()", namespaces=namespaces)
        
        if org_id and party_type_code:
            party_data = {
                "id": org_id[0],
                "details": {
                    "classifications": [
                        {
                            "scheme": "eu-buyer-contracting-type",
                            "id": party_type_code[0],
                            "description": buyer_contracting_type_mapping.get(party_type_code[0], "Unknown")
                        }
                    ]
                },
                "roles": ["buyer"]
            }
            result["parties"].append(party_data)

    return result if result["parties"] else None

def merge_buyer_contracting_entity(release_json, buyer_contracting_entity_data):
    """
    Merge the parsed buyer contracting entity data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        buyer_contracting_entity_data (dict): The parsed buyer contracting entity data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not buyer_contracting_entity_data:
        logger.warning("No buyer contracting entity data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in buyer_contracting_entity_data["parties"]:
        existing_party = next((party for party in parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_details = existing_party.setdefault("details", {})
            existing_classifications = existing_details.setdefault("classifications", [])
            new_classification = new_party["details"]["classifications"][0]
            existing_classification = next((c for c in existing_classifications if c["scheme"] == new_classification["scheme"]), None)
            if existing_classification:
                existing_classification.update(new_classification)
            else:
                existing_classifications.append(new_classification)
            
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
        else:
            parties.append(new_party)

    logger.info(f"Merged buyer contracting entity data for {len(buyer_contracting_entity_data['parties'])} parties")