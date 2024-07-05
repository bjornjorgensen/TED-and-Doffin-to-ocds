# converters/BT_165_Organization_Company.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_winner_size(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    
    for org in organizations:
        org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        company_size = org.xpath("efac:Company/efbc:CompanySizeCode[@listName='economic-operator-size']/text()", namespaces=namespaces)
        
        if org_id and company_size:
            result["parties"].append({
                "id": org_id[0],
                "details": {
                    "scale": company_size[0]
                }
            })

    return result if result["parties"] else None

def merge_winner_size(release_json, winner_size_data):
    if not winner_size_data:
        logger.warning("No Winner Size data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in winner_size_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("details", {})["scale"] = new_party["details"]["scale"]
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Winner Size data for {len(winner_size_data['parties'])} parties")