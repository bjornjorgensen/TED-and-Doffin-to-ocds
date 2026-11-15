"""BT-01(e) Procedure Legal Basis (NoID) converter.

Maps the ``LocalLegalBasis`` identifier, used when the legal basis has no
identifier, to OCDS ``tender.legalBasis.id``.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

LOCAL_LEGAL_BASIS = "LocalLegalBasis"

XPATH_LOCAL_LEGAL_BASIS_ID = (
    "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference"
    f"[cbc:ID/text()='{LOCAL_LEGAL_BASIS}']/cbc:ID"
)


def parse_procedure_legal_basis_noid(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the procedure legal basis without an ID (BT-01(e)) from XML content.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Dictionary containing the legal basis ID, or None if no data is found.
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        legal_basis_ids = root.xpath(XPATH_LOCAL_LEGAL_BASIS_ID, namespaces=NAMESPACES)
        if not legal_basis_ids or not legal_basis_ids[0].text:
            logger.info("No procedure Legal Basis (NoID) data found")
            return None

        logger.info("Parsed procedure Legal Basis (NoID) data")
        return {"tender": {"legalBasis": {"id": legal_basis_ids[0].text}}}

    except etree.XMLSyntaxError:
        logger.exception("XML parsing error")
        return None
    except Exception:
        logger.exception("Error parsing procedure legal basis NoID")
        return None


def merge_procedure_legal_basis_noid(
    release_json: dict[str, Any], legal_basis_data: dict[str, Any] | None
) -> None:
    """Merge the legal basis NoID data into the release JSON.

    Args:
        release_json: The release JSON to update
        legal_basis_data: The legal basis NoID data to merge
    """
    if not legal_basis_data:
        return

    tender = release_json.setdefault("tender", {})
    legal_basis = tender.setdefault("legalBasis", {})
    legal_basis.update(legal_basis_data["tender"]["legalBasis"])
    logger.info("Merged procedure Legal Basis (NoID) data")
