"""Converter for 2015 TED XML notice type information.

This module handles extraction of notice type information from 2015 format TED notices
and maps it to appropriate OCDS tags and tender status.
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_notice_type_2015(xml_content: str | bytes) -> dict | None:
    """Parse notice type information from 2015 format TED notice.

    Maps notice types to appropriate tags and status:
    - PRI_ONLY/PRI_REDUCING_TIME_LIMITS: tag="planning", status="planned"
    - PRI_CALL_COMPETITION: tags=["planning","tender"], status="active"

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "tag": [str],  # List of tags
                "tender": {
                    "status": str  # Tender status
                }
            }
        Returns None if not a handled notice type

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        notice_type = root.xpath("/NOTICE/@TYPE")
        if not notice_type:
            return None

        notice_type = notice_type[0]
        if notice_type in ("PRI_ONLY", "PRI_REDUCING_TIME_LIMITS"):
            return {"tag": ["planning"], "tender": {"status": "planned"}}
        if notice_type == "PRI_CALL_COMPETITION":
            return {"tag": ["planning", "tender"], "tender": {"status": "active"}}

        return None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing notice type")
        return None


def merge_notice_type_2015(release_json: dict, notice_type_data: dict | None) -> None:
    """Merge notice type data into the OCDS release.

    Updates tag list and tender.status based on notice type information.

    Args:
        release_json: Target release JSON to update
        notice_type_data: Notice type data in format:
            {
                "tag": [str],
                "tender": {
                    "status": str
                }
            }

    Note:
        Updates release_json in-place

    """
    if not notice_type_data:
        return

    # Add planning tag if not present
    tags = release_json.setdefault("tag", [])
    for tag in notice_type_data["tag"]:
        if tag not in tags:
            tags.append(tag)

    # Update tender status
    tender = release_json.setdefault("tender", {})
    tender["status"] = notice_type_data["tender"]["status"]

    logger.info(
        "Merged notice type data - tags: %s, status: %s",
        notice_type_data["tag"],
        notice_type_data["tender"]["status"],
    )
