# converters/bt_01d_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_legal_basis_description(xml_content):
    """
    Parse the XML content to extract the legal basis description.

    Maps BT-01(d): The legal basis description.
    XPath: /*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[not(cbc:ID/text()=('CrossBorderLaw','LocalLegalBasis'))]/cbc:DocumentDescription
    """
    logger.info("Starting parse_procedure_legal_basis_description")

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

    # First find all legal references that aren't CrossBorderLaw or LocalLegalBasis
    refs = root.xpath(
        ".//cac:ProcurementLegislationDocumentReference[not(cbc:ID[text()='CrossBorderLaw' or text()='LocalLegalBasis'])]",
        namespaces=namespaces,
    )

    logger.info("Found %d valid references", len(refs))

    # Then look for descriptions in those references
    for ref in refs:
        desc_elem = ref.find("cbc:DocumentDescription", namespaces=namespaces)
        if desc_elem is not None and desc_elem.text and desc_elem.text.strip():
            description = desc_elem.text.strip()
            logger.info("Found description: %s", description)
            return {"tender": {"legalBasis": {"description": description}}}

    logger.info("No valid description found")
    return None


def merge_procedure_legal_basis_description(release_json, description_data):
    """
    Merge the parsed legal basis description into the main OCDS release JSON.
    """
    logger.info("Starting merge with data: %s", description_data)
    if not description_data:
        logger.info("No description data to merge")
        return

    try:
        tender = release_json.setdefault("tender", {})
        legal_basis = tender.setdefault("legalBasis", {})

        description = description_data["tender"]["legalBasis"]["description"]
        legal_basis["description"] = description
        logger.info("Successfully merged description: %s", description)
    except Exception:
        logger.exception("Error merging description: %s")
