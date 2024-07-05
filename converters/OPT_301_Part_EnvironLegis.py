# converters/OPT_301_Part_EnvironLegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_part_environlegis(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": [], "tender": {"documents": []}}

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference"
    environ_legis_refs = root.xpath(xpath, namespaces=namespaces)

    for ref in environ_legis_refs:
        doc_id = ref.xpath("cbc:ID/text()", namespaces=namespaces)
        org_id = ref.xpath("cac:IssuerParty/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)

        if doc_id and org_id:
            doc_id = doc_id[0]
            org_id = org_id[0]

            result["tender"]["documents"].append({
                "id": doc_id,
                "publisher": {"id": org_id}
            })

            result["parties"].append({
                "id": org_id,
                "roles": ["informationService"]
            })

    return result if (result["parties"] or result["tender"]["documents"]) else None

def merge_part_environlegis(release_json, environlegis_data):
    if not environlegis_data:
        logger.warning("No Part Environmental Legislation data to merge")
        return

    # Merge parties
    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in environlegis_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    # Merge documents
    existing_docs = {doc["id"]: doc for doc in release_json.get("tender", {}).get("documents", [])}
    for doc in environlegis_data["tender"]["documents"]:
        if doc["id"] in existing_docs:
            existing_docs[doc["id"]]["publisher"] = doc["publisher"]
        else:
            release_json.setdefault("tender", {}).setdefault("documents", []).append(doc)

    logger.info(f"Merged Part Environmental Legislation data for {len(environlegis_data['parties'])} parties and {len(environlegis_data['tender']['documents'])} documents")