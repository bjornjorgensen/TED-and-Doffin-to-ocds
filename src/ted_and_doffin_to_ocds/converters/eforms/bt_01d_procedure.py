"""BT-01(d) Procedure Legal Basis (Description) converter.

Maps the description of the legal basis under which the procurement procedure
takes place to OCDS ``tender.legalBasis.description``.
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

# XPath 1.0 has no sequence comparison, so the excluded IDs are compared one by one.
XPATH_LEGAL_BASIS_DESCRIPTION = (
    "/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference"
    f"[not(cbc:ID/text()='{CROSS_BORDER_LAW}' or cbc:ID/text()='{LOCAL_LEGAL_BASIS}')]"
    "/cbc:DocumentDescription"
)


def parse_procedure_legal_basis_description(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the procedure legal basis description (BT-01(d)) from XML content.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Dictionary containing the legal basis description and its translations,
        or None if no data is found.
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        descriptions = root.xpath(XPATH_LEGAL_BASIS_DESCRIPTION, namespaces=NAMESPACES)
        if not descriptions:
            logger.info("No procedure Legal Basis (Description) data found")
            return None

        legal_basis: dict[str, Any] = {}
        if descriptions[0].text is not None:
            legal_basis["description"] = descriptions[0].text

        multilingual_descriptions = [
            {"language": description.get("languageID"), "text": description.text}
            for description in descriptions
            if description.get("languageID")
        ]
        if multilingual_descriptions:
            legal_basis["multilingualDescriptions"] = multilingual_descriptions

        if not legal_basis:
            logger.info("No procedure Legal Basis (Description) data found")
            return None

    except etree.XMLSyntaxError:
        logger.exception("XML parsing error")
        return None
    except Exception:
        logger.exception("Error parsing procedure legal basis description")
        return None
    else:
        logger.info("Parsed procedure Legal Basis (Description) data")
        return {"tender": {"legalBasis": legal_basis}}


def merge_procedure_legal_basis_description(
    release_json: dict[str, Any], legal_basis_data: dict[str, Any] | None
) -> None:
    """Merge the legal basis description data into the release JSON.

    Args:
        release_json: The release JSON to update
        legal_basis_data: The legal basis description data to merge
    """
    if not legal_basis_data:
        return

    tender = release_json.setdefault("tender", {})
    legal_basis = tender.setdefault("legalBasis", {})
    legal_basis.update(legal_basis_data["tender"]["legalBasis"])
    logger.info("Merged procedure Legal Basis (Description) data")
