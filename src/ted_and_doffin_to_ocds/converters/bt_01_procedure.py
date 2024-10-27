# converters/bt_01_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_legal_basis(xml_content):
    """
    Parse the XML content to extract the legal basis under which the procurement procedure takes place.
    Only processes IDs with schemeName="ELI"
    """
    logger.info("Starting parse_procedure_legal_basis")

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

    # Use a simpler XPath first to get all references
    refs = root.xpath(
        ".//cac:ProcurementLegislationDocumentReference/cbc:ID[@schemeName='ELI']",
        namespaces=namespaces,
    )

    logger.info("Found %d references with ELI scheme", len(refs))

    for ref in refs:
        id_value = ref.text.strip()
        logger.info("Processing reference: %s", id_value)

        if id_value not in ("CrossBorderLaw", "LocalLegalBasis"):
            logger.info("Found valid legal basis: %s", id_value)
            return {"tender": {"legalBasis": {"scheme": "ELI", "id": id_value}}}

    logger.info("No valid legal basis found")
    return None


def merge_procedure_legal_basis(release_json, legal_basis_data):
    """
    Merge the parsed legal basis data into the main OCDS release JSON.
    """
    logger.info("Starting merge with data: %s", legal_basis_data)
    if not legal_basis_data:
        logger.info("No legal basis data to merge")
        return

    try:
        tender = release_json.setdefault("tender", {})
        legal_basis = legal_basis_data["tender"]["legalBasis"]
        tender["legalBasis"] = legal_basis
        logger.info("Successfully merged legal basis: %s", legal_basis)
    except Exception:
        logger.exception("Error merging legal basis: %s")
