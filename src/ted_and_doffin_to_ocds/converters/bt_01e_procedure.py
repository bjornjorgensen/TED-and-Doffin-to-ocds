# converters/bt_01e_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_legal_basis_noid(xml_content):
    """
    Parse the XML content to extract the local legal basis ID.

    Maps BT-01(e): The legal basis NoID.
    XPath: /*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='LocalLegalBasis']/cbc:ID
    """
    logger.info("Starting parse_procedure_legal_basis_noid")

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

    xpath = ".//cac:ProcurementLegislationDocumentReference[cbc:ID/text()='LocalLegalBasis']/cbc:ID"
    refs = root.xpath(xpath, namespaces=namespaces)

    logger.info("Found %d local legal basis references", len(refs))

    if refs:
        # Return first found LocalLegalBasis ID
        logger.info("Found local legal basis: LocalLegalBasis")
        return {"tender": {"legalBasis": {"id": "LocalLegalBasis"}}}

    logger.info("No local legal basis found")
    return None


def merge_procedure_legal_basis_noid(release_json, noid_data):
    """
    Merge the parsed legal basis NoID into the main OCDS release JSON.
    """
    logger.info("Starting merge with data: %s", noid_data)
    if not noid_data:
        logger.info("No NoID data to merge")
        return

    try:
        tender = release_json.setdefault("tender", {})
        legal_basis = tender.setdefault("legalBasis", {})

        legal_basis["id"] = noid_data["tender"]["legalBasis"]["id"]
        logger.info("Successfully merged legal basis NoID")
    except Exception:
        logger.exception("Error merging legal basis NoID: %s")
