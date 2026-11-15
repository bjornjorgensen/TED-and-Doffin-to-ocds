"""BT-01(c) Procedure Legal Basis (ID) converter.

Maps the identifier of the legal basis under which the procurement procedure
takes place to OCDS ``tender.legalBasis.id`` and ``tender.legalBasis.scheme``.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

CROSS_BORDER_LAW = "CrossBorderLaw"
LOCAL_LEGAL_BASIS = "LocalLegalBasis"
# The mapping only names the http variant, but ELI URIs are published with both.
ELI_PREFIXES = (
    "http://data.europa.eu/eli/dir",
    "https://data.europa.eu/eli/dir",
)
ELI_SCHEME = "ELI"

# XPath 1.0 has no sequence comparison, so the excluded IDs are compared one by one.
XPATH_LEGAL_BASIS_ID = (
    "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference"
    f"[not(cbc:ID/text()='{CROSS_BORDER_LAW}' or cbc:ID/text()='{LOCAL_LEGAL_BASIS}')]/cbc:ID"
)


def parse_procedure_legal_basis_id(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the procedure legal basis ID (BT-01(c)) from XML content.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Dictionary containing the legal basis ID and scheme, or None if no data
        is found.
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        legal_basis_ids = root.xpath(XPATH_LEGAL_BASIS_ID, namespaces=NAMESPACES)
        if not legal_basis_ids or not legal_basis_ids[0].text:
            logger.info("No procedure Legal Basis (ID) data found")
            return None

        legal_basis_id = legal_basis_ids[0].text
        legal_basis: dict[str, Any] = {"id": legal_basis_id}
        # An ELI URI identifies its own scheme, so the scheme is only taken from
        # the schemeName attribute when the value is not an ELI URI.
        scheme = legal_basis_ids[0].get("schemeName")
        if not scheme and legal_basis_id.startswith(ELI_PREFIXES):
            scheme = ELI_SCHEME
        if scheme:
            legal_basis["scheme"] = scheme

    except etree.XMLSyntaxError:
        logger.exception("XML parsing error")
        return None
    except Exception:
        logger.exception("Error parsing procedure legal basis ID")
        return None
    else:
        logger.info("Parsed procedure Legal Basis (ID) data")
        return {"tender": {"legalBasis": legal_basis}}


def merge_procedure_legal_basis_id(
    release_json: dict[str, Any], legal_basis_data: dict[str, Any] | None
) -> None:
    """Merge the legal basis ID data into the release JSON.

    Args:
        release_json: The release JSON to update
        legal_basis_data: The legal basis ID data to merge
    """
    if not legal_basis_data:
        return

    tender = release_json.setdefault("tender", {})
    legal_basis = tender.setdefault("legalBasis", {})
    legal_basis.update(legal_basis_data["tender"]["legalBasis"])
    logger.info("Merged procedure Legal Basis (ID) data")
