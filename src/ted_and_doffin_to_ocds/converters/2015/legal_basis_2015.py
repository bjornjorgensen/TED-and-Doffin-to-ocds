"""Converter for legal basis information from 2015 TED format.

This module handles mapping of legal basis references (CELEX numbers) from
2015 format TED notices to OCDS tender.legalBasis, including both primary
and other legal bases.
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_legal_basis_2015(xml_content: str | bytes) -> dict | None:
    """Parse legal basis from 2015 format TED notice.

    Gets the CELEX number from either LEGAL_BASIS or LEGAL_BASIS_OTHER element
    and maps it to tender.legalBasis with scheme 'CELEX'.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "tender": {
                    "legalBasis": {
                        "scheme": "CELEX",
                        "id": str  # CELEX number
                    }
                }
            }
        Returns None if no legal basis found

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        # Check both LEGAL_BASIS and LEGAL_BASIS_OTHER elements
        legal_basis = root.find("LEGAL_BASIS")
        if legal_basis is None or not legal_basis.text:
            legal_basis = root.find("LEGAL_BASIS_OTHER")

        if legal_basis is not None and legal_basis.text:
            return {
                "tender": {
                    "legalBasis": {"scheme": "CELEX", "id": legal_basis.text.strip()}
                }
            }
        return None  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing legal basis")
        return None


def merge_legal_basis_2015(release_json: dict, legal_basis_data: dict | None) -> None:
    """Merge legal basis data into the OCDS release.

    Updates tender.legalBasis with the CELEX scheme and number.

    Args:
        release_json: Target release JSON to update
        legal_basis_data: Legal basis data in format:
            {
                "tender": {
                    "legalBasis": {
                        "scheme": "CELEX",
                        "id": str
                    }
                }
            }

    Note:
        Updates release_json in-place

    """
    if not legal_basis_data:
        logger.warning("No legal basis data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender["legalBasis"] = legal_basis_data["tender"]["legalBasis"]

    logger.info(
        "Merged legal basis: %s", legal_basis_data["tender"]["legalBasis"]["id"]
    )
