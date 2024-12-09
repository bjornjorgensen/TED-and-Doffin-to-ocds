"""Converter for official name information from 2015 TED format.

This module handles mapping of contracting authority official names from 2015 format
TED notices to OCDS party names and legal names.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_official_name_2015(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse contracting authority official name from 2015 format TED notice.

    Maps OFFICIALNAME to both party.name and party.identifier.legalName.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "parties": [
                    {
                        "id": str,  # Organization ID
                        "name": str,  # Official name
                        "identifier": {
                            "legalName": str  # Same official name
                        }
                    }
                ]
            }
        Returns None if no official name found

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        body = root.find(".//CONTRACTING_BODY/ADDRESS_CONTRACTING_BODY")
        if body is not None:
            org_id = body.findtext("ORGANISATION") or "unknown"
            official_name = body.findtext("OFFICIALNAME")

            if official_name:
                return {
                    "parties": [
                        {
                            "id": org_id,
                            "name": official_name,
                            "identifier": {"legalName": official_name},
                        }
                    ]
                }
        return None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing official name")
        return None


def merge_official_name_2015(
    release_json: dict, official_name_data: dict | None
) -> None:
    """Merge official name data into the OCDS release.

    Updates party name and identifier.legalName with the official name.

    Args:
        release_json: Target release JSON to update
        official_name_data: Official name data to merge in format:
            {
                "parties": [
                    {
                        "id": str,
                        "name": str,
                        "identifier": {
                            "legalName": str
                        }
                    }
                ]
            }

    Note:
        Updates release_json in-place

    """
    if not official_name_data:
        logger.warning("No official name data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for new_party in official_name_data["parties"]:
        existing_party = next((p for p in parties if p["id"] == new_party["id"]), None)
        if existing_party:
            existing_party["name"] = new_party["name"]
            identifier = existing_party.setdefault("identifier", {})
            identifier["legalName"] = new_party["identifier"]["legalName"]
        else:
            parties.append(new_party)

    logger.info("Merged official name data")
