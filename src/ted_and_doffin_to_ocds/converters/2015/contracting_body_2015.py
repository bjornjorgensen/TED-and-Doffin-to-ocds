"""Converter for contracting body information from 2015 TED format.

This module handles mapping of contracting authority information from 2015 format
TED notices to OCDS parties and buyer fields.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_contracting_body_2015(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse contracting body information from 2015 format TED notice.

    Extracts contracting authority details from ADDRESS_CONTRACTING_BODY element,
    creating corresponding party entries and buyer references.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "parties": [
                    {
                        "id": str,  # Organization ID
                        "name": str, # Organization name
                        "roles": ["buyer"]
                    }
                ],
                "buyer": {
                    "id": str,  # Same as party.id
                    "name": str  # Same as party.name
                }
            }
        Returns None if no contracting body found

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        body = root.find(".//CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY")
        if body is not None:
            # Get organization ID and name
            org_id = body.findtext("ORGANISATION") or "unknown"
            org_name = body.findtext("OFFICIALNAME") or org_id

            return {
                "parties": [{"id": org_id, "name": org_name, "roles": ["buyer"]}],
                "buyer": {"id": org_id, "name": org_name},
            }
        return None  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing contracting body")
        return None


def merge_contracting_body_2015(
    release_json: dict, contracting_body_data: dict[str, Any] | None
) -> None:
    """Merge contracting body data into the OCDS release.

    Updates parties array with buyer information and sets the main buyer reference.

    Args:
        release_json: Target release JSON to update
        contracting_body_data: Contracting body data in format:
            {
                "parties": [...],
                "buyer": {...}
            }

    Note:
        Updates release_json in-place

    """
    if not contracting_body_data:
        logger.warning("No contracting body data to merge")
        return

    # Add/update parties
    parties = release_json.setdefault("parties", [])
    for new_party in contracting_body_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)
        if existing_party:
            if "buyer" not in existing_party["roles"]:
                existing_party["roles"].append("buyer")
        else:
            parties.append(new_party)

    # Set buyer reference
    release_json["buyer"] = contracting_body_data["buyer"]

    logger.info("Merged contracting body data")
