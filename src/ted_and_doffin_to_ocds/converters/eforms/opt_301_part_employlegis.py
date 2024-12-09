# converters/opt_301_part_employlegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_employment_legislation_org_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse employment legislation organization references from parts.

    For each employment legislation document:
    - Gets document publisher organization ID
    - Adds informationService role to publisher organizations
    - Links documents to publishers

    Args:
        xml_content: XML content containing part data

    Returns:
        Optional[Dict]: Dictionary containing parties and documents, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["informationService"]
                }
            ],
            "tender": {
                "documents": [
                    {
                        "id": "doc_id",
                        "publisher": {"id": "org_id"}
                    }
                ]
            }
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:EmploymentLegislationDocumentReference"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No employment legislation organization reference data found. Skipping parse_employment_legislation_org_reference."
        )
        return None

    result = {"parties": [], "tender": {"documents": []}}

    employment_legislation_refs = root.xpath(relevant_xpath, namespaces=namespaces)
    for ref in employment_legislation_refs:
        doc_id = ref.xpath("cbc:ID/text()", namespaces=namespaces)
        org_id = ref.xpath(
            "cac:IssuerParty/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )

        if doc_id and org_id:
            result["parties"].append({"id": org_id[0], "roles": ["informationService"]})
            result["tender"]["documents"].append(
                {"id": doc_id[0], "publisher": {"id": org_id[0]}}
            )

    return result if (result["parties"] or result["tender"]["documents"]) else None


def merge_employment_legislation_org_part(
    release_json: dict[str, Any], parsed_data: dict[str, Any] | None
) -> None:
    """Merge employment legislation organization data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        parsed_data: Employment legislation data containing organizations and documents

    Effects:
        - Updates parties with informationService roles
        - Updates documents with publisher references
        - Maintains existing data while adding new information

    """
    if not parsed_data:
        logger.info("No employment legislation organization reference data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for new_party in parsed_data.get("parties", []):
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
    for new_doc in parsed_data.get("tender", {}).get("documents", []):
        existing_doc = next(
            (doc for doc in tender_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["publisher"] = new_doc["publisher"]
        else:
            tender_documents.append(new_doc)

    logger.info("Merged employment legislation organization reference data")
