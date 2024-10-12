# converters/opt_301_part_environlegis.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_environmental_legislation_org_reference(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": [], "tender": {"documents": []}}

    env_leg_refs = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference",
        namespaces=namespaces,
    )

    for ref in env_leg_refs:
        doc_id = ref.xpath("cbc:ID/text()", namespaces=namespaces)
        org_id = ref.xpath(
            "cac:IssuerParty/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )

        if doc_id and org_id:
            result["tender"]["documents"].append(
                {"id": doc_id[0], "publisher": {"id": org_id[0]}}
            )

            if not any(party["id"] == org_id[0] for party in result["parties"]):
                result["parties"].append(
                    {"id": org_id[0], "roles": ["informationService"]}
                )

    return result if (result["parties"] or result["tender"]["documents"]) else None


def merge_environmental_legislation_org_reference(release_json, parsed_data):
    if not parsed_data:
        return

    parties = release_json.setdefault("parties", [])
    for new_party in parsed_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_party.setdefault("roles", []).extend(
                role
                for role in new_party["roles"]
                if role not in existing_party["roles"]
            )
        else:
            parties.append(new_party)

    tender_documents = release_json.setdefault("tender", {}).setdefault("documents", [])
    for new_doc in parsed_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in tender_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["publisher"] = new_doc["publisher"]
        else:
            tender_documents.append(new_doc)

    logger.info("Merged environmental legislation organization reference data")
