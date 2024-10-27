# converters/bt_01_notice.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_legal_basis_regulatory(xml_content):
    """
    Parse the XML content to extract the regulatory domain legal basis.

    Maps BT-01-notice: The legal basis regulatory domain.
    XPath: /*/cbc:RegulatoryDomain
    Maps to tender.legalBasis.id with scheme="CELEX"
    Should not overwrite existing ELI scheme.
    """
    logger.info("Starting parse_procedure_legal_basis_regulatory")

    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        logger.info("XML root tag: %s", root.tag)
    except Exception:
        logger.exception("Failed to parse XML")
        return None

    namespaces = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    }

    xpath = "./cbc:RegulatoryDomain"
    refs = root.xpath(xpath, namespaces=namespaces)

    logger.info("Found %d regulatory domains", len(refs))

    if refs:
        domain = refs[0].text.strip()
        if domain:
            logger.info("Found regulatory domain: %s", domain)
            return {"tender": {"legalBasis": {"scheme": "CELEX", "id": domain}}}

    logger.info("No valid regulatory domain found")
    return None


def merge_procedure_legal_basis_regulatory(release_json, regulatory_data):
    """
    Merge the parsed regulatory domain legal basis into the main OCDS release JSON.
    Will not overwrite if there's already an ELI scheme present.
    """
    logger.info("Starting merge with data: %s", regulatory_data)
    if not regulatory_data:
        logger.info("No regulatory domain data to merge")
        return

    try:
        tender = release_json.setdefault("tender", {})
        legal_basis = tender.get("legalBasis", {})

        # Only merge if there's no ELI scheme already present
        if legal_basis.get("scheme") != "ELI":
            logger.info("No ELI scheme found, merging CELEX data")
            tender["legalBasis"] = regulatory_data["tender"]["legalBasis"]
        else:
            logger.info("Found existing ELI scheme, skipping CELEX data")

    except Exception:
        logger.exception("Error merging regulatory domain")
