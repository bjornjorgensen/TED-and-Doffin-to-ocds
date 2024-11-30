# converters/opt_301_part_employlegis.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def part_parse_employment_legislation_org_reference(xml_content):
    """
    Parse the XML content to extract the employment legislation organization reference.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed employment legislation organization reference data.
        None: If no relevant data is found.
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


def part_merge_employment_legislation_org_reference(release_json, parsed_data) -> None:
    """
    Merge the parsed employment legislation organization reference data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        parsed_data (dict): The parsed employment legislation organization reference data to be merged.

    Returns:
        None: The function updates the release_json in-place.
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
