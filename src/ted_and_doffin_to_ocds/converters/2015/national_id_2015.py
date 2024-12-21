"""Converter for national registration numbers from 2015 TED format.

This module handles mapping of national registration numbers from ADDRESS_CONTRACTING_BODY
to OCDS party identifiers.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_national_id_2015(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse national registration number from 2015 format TED notice.

    Maps NATIONALID to party.identifier fields with scheme 'EU-NAT'.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "parties": [
                    {
                        "id": str,  # Organization ID
                        "identifier": {
                            "scheme": "EU-NAT",
                            "id": str  # National registration number
                        }
                    }
                ]
            }
        Returns None if no national ID found

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        body = root.find(".//CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY")
        if body is not None:
            org_id = body.findtext("ORGANISATION") or "unknown"
            national_id = body.findtext("NATIONALID")

            if national_id:
                return {
                    "parties": [
                        {
                            "id": org_id,
                            "identifier": {"scheme": "EU-NAT", "id": national_id},
                        }
                    ]
                }
        return None  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing national ID")
        return None


def merge_national_id_2015(release_json: dict, national_id_data: dict | None) -> None:
    """Merge national registration number into the OCDS release.

    Updates party identifier fields with national registration information.

    Args:
        release_json: Target release JSON to update
        national_id_data: National ID data in format:
            {
                "parties": [
                    {
                        "id": str,
                        "identifier": {
                            "scheme": str,
                            "id": str
                        }
                    }
                ]
            }

    Note:
        Updates release_json in-place

    """
    if not national_id_data:
        logger.warning("No national ID data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for new_party in national_id_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)
        if existing_party:
            identifier = existing_party.setdefault("identifier", {})
            identifier.update(new_party["identifier"])
        else:
            parties.append(new_party)

    logger.info("Merged national ID data")
