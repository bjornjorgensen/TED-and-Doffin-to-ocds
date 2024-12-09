"""Converter for address information from 2015 TED format.

This module handles mapping of postal addresses from ADDRESS_CONTRACTING_BODY
to OCDS party address fields.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_address_2015(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse postal address from 2015 format TED notice.

    Maps ADDRESS element content to party.address.streetAddress.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "parties": [
                    {
                        "id": str,  # Organization ID
                        "address": {
                            "streetAddress": str  # Postal address
                        }
                    }
                ]
            }
        Returns None if no address found

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        body = root.find(".//CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY")
        if body is not None:
            org_id = body.findtext("ORGANISATION") or "unknown"
            address = body.findtext("ADDRESS")

            if address:
                return {
                    "parties": [{"id": org_id, "address": {"streetAddress": address}}]
                }
        return None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing address")
        return None


def merge_address_2015(release_json: dict, address_data: dict | None) -> None:
    """Merge postal address into the OCDS release.

    Updates party address fields with street address information.

    Args:
        release_json: Target release JSON to update
        address_data: Address data in format:
            {
                "parties": [
                    {
                        "id": str,
                        "address": {
                            "streetAddress": str
                        }
                    }
                ]
            }

    Note:
        Updates release_json in-place

    """
    if not address_data:
        logger.warning("No address data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for new_party in address_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)
        if existing_party:
            address = existing_party.setdefault("address", {})
            address.update(new_party["address"])
        else:
            parties.append(new_party)

    logger.info("Merged address data")
