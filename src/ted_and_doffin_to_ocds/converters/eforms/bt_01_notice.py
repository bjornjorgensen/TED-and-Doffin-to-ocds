"""BT-01-notice Procedure Legal Basis (Regulatory Domain) converter.

Maps the CELEX number of the regulatory domain to OCDS
``tender.legalBasis.wasDerivedFrom``.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

OTHER_VALUE = "other"
CELEX_SCHEME = "CELEX"

XPATH_REGULATORY_DOMAIN = "/*/cbc:RegulatoryDomain"


def parse_procedure_legal_basis_regulatory_domain(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the procedure legal basis regulatory domain (BT-01-notice) from XML.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Dictionary containing the CELEX identifier the legal basis is derived
        from, or None if no data is found.
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        regulatory_domains = root.xpath(XPATH_REGULATORY_DOMAIN, namespaces=NAMESPACES)
        if not regulatory_domains:
            logger.info("No procedure Legal Basis (Regulatory Domain) data found")
            return None

        regulatory_domain = regulatory_domains[0].text
        if not regulatory_domain or regulatory_domain == OTHER_VALUE:
            logger.info("No procedure Legal Basis (Regulatory Domain) data found")
            return None

        legal_basis = {
            "wasDerivedFrom": {
                "scheme": CELEX_SCHEME,
                "id": regulatory_domain,
            },
        }

    except etree.XMLSyntaxError:
        logger.exception("XML parsing error")
        return None
    except Exception:
        logger.exception("Error parsing procedure legal basis regulatory domain")
        return None
    else:
        logger.info("Parsed procedure Legal Basis (Regulatory Domain) data")
        return {"tender": {"legalBasis": legal_basis}}


def merge_procedure_legal_basis_regulatory_domain(
    release_json: dict[str, Any], legal_basis_data: dict[str, Any] | None
) -> None:
    """Merge the legal basis regulatory domain data into the release JSON.

    Args:
        release_json: The release JSON to update
        legal_basis_data: The legal basis regulatory domain data to merge
    """
    if not legal_basis_data:
        return

    tender = release_json.setdefault("tender", {})
    legal_basis = tender.setdefault("legalBasis", {})
    legal_basis.update(legal_basis_data["tender"]["legalBasis"])
    logger.info("Merged procedure Legal Basis (Regulatory Domain) data")
