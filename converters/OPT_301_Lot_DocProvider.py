# converters/OPT_301_Lot_DocProvider.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_document_provider_identifier(xml_content):
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

    document_providers = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:DocumentProviderParty/cac:PartyIdentification/cbc:ID", namespaces=namespaces)
    
    for provider in document_providers:
        party = {
            "id": provider.text,
            "roles": ["processContactPoint"]
        }
        result["parties"].append(party)

    return result if result["parties"] else None

def merge_document_provider_identifier(release_json, document_provider_data):
    if not document_provider_data:
        logger.warning("No Document Provider Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in document_provider_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            if "processContactPoint" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("processContactPoint")
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Document Provider Identifier data for {len(document_provider_data['parties'])} parties")