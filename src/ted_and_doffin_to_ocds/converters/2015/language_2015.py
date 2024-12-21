"""Converter for 2015 regulation language codes.

This module handles mapping of language codes from the 2015 TED XML format
to standard ISO language codes.
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_language_2015(xml_content: str | bytes) -> dict | None:
    """Parse language code from 2015 format TED notice.

    Gets the language code from @LG attribute on root element and converts
    to lowercase.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Dictionary in format:
            {
                "language": str  # Lowercase language code
            }
        Returns None if no language code found

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        lang_code = root.get("LG")
        if lang_code:
            return {"language": lang_code.lower()}

        return None  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing language code")
        return None


def merge_language_2015(release_json: dict, language_data: dict | None) -> None:
    """Merge language code into the OCDS release.

    Updates language field with the lowercase language code.

    Args:
        release_json: Target release JSON to update
        language_data: Language data to merge in format:
            {
                "language": str  # Lowercase language code
            }

    Note:
        Updates release_json in-place

    """
    if not language_data:
        logger.warning("No language data to merge")
        return

    release_json["language"] = language_data["language"]
    logger.info("Merged language code: %s", language_data["language"])
