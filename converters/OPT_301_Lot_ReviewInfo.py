# converters/OPT_301_Lot_ReviewInfo.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_review_info_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AppealTerms/cac:AppealInformationParty/cac:PartyIdentification/cbc:ID"
    review_info_ids = root.xpath(xpath_query, namespaces=namespaces)

    for review_info_id in review_info_ids:
        party = {
            "id": review_info_id.text,
            "roles": ["reviewContactPoint"]
        }
        result["parties"].append(party)

    return result if result["parties"] else None

def merge_review_info_identifier(release_json, review_info_data):
    if not review_info_data:
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in review_info_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            if "reviewContactPoint" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewContactPoint")
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged review info provider data for {len(review_info_data['parties'])} parties")