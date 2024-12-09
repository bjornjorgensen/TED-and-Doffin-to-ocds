"""Converter for town information from 2015 TED format.

This module handles mapping of town/city names from ADDRESS_CONTRACTING_BODY
to OCDS party address locality fields.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_town_2015(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse town information from 2015 format TED notice.

    Maps TOWN element to party.address.locality.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "parties": [
                    {
                        "id": str,  # Organization ID
                        "address": {
                            "locality": str  # Town/city name
                        }
                    }
                ]
            }
        Returns None if no town found

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        body = root.find(".//CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY")
        if body is not None:
            org_id = body.findtext("ORGANISATION") or "unknown"
            town = body.findtext("TOWN")

            if town:
                return {"parties": [{"id": org_id, "address": {"locality": town}}]}
        return None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing town")
        return None


def merge_town_2015(release_json: dict, town_data: dict | None) -> None:
    """Merge town information into the OCDS release.

    Updates party address fields with locality information.

    Args:
        release_json: Target release JSON to update
        town_data: Town data in format:
            {
                "parties": [
                    {
                        "id": str,
                        "address": {
                            "locality": str
                        }
                    }
                ]
            }

    Note:
        Updates release_json in-place

    """
    if not town_data:
        logger.warning("No town data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for new_party in town_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)
        if existing_party:
            address = existing_party.setdefault("address", {})
            address.update(new_party["address"])
        else:
            parties.append(new_party)

    logger.info("Merged town data")
