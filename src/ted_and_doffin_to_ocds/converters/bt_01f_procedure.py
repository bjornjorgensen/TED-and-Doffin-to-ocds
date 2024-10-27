# converters/bt_01f_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_legal_basis_noid_description(xml_content):
    """
    Parse the XML content to extract the description for local legal basis.

    Maps BT-01(f): The legal basis NoID Description.
    XPath: /*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='LocalLegalBasis']/cbc:DocumentDescription
    """
    logger.info("Starting parse_procedure_legal_basis_noid_description")

    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        logger.info("XML root tag: %s", root.tag)
    except Exception:
        logger.exception("Failed to parse XML: %s")
        return None

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Find references with LocalLegalBasis ID
    xpath = ".//cac:ProcurementLegislationDocumentReference[cbc:ID/text()='LocalLegalBasis']/cbc:DocumentDescription"
    refs = root.xpath(xpath, namespaces=namespaces)

    logger.info("Found %d document descriptions", len(refs))

    if refs:
        for desc in refs:
            if desc.text and desc.text.strip():
                description = desc.text.strip()
                logger.info("Found description: %s", description)
                return {"tender": {"legalBasis": {"description": description}}}

    logger.info("No valid description found")
    return None


def merge_procedure_legal_basis_noid_description(release_json, description_data):
    """
    Merge the parsed legal basis NoID description into the main OCDS release JSON.
    """
    logger.info("Starting merge with data: %s", description_data)
    if not description_data:
        logger.info("No NoID description data to merge")
        return

    try:
        tender = release_json.setdefault("tender", {})
        legal_basis = tender.setdefault("legalBasis", {})

        description = description_data["tender"]["legalBasis"]["description"]
        legal_basis["description"] = description
        logger.info("Successfully merged description: %s", description)
    except Exception:
        logger.exception("Error merging NoID description: %s")
