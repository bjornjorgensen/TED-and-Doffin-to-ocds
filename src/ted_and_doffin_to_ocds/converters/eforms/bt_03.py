"""BT-03 Form Type converter.

This module handles conversion of procurement notice form types to OCDS format.
It maps the form types specified in EU Vocabularies to corresponding OCDS tags and tender statuses.
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)

form_type_mapping: dict[str, dict[str, list[str] | str | None]] = {
    "planning": {"tag": ["tender"], "status": "planned"},
    "competition": {"tag": ["tender"], "status": "active"},
    "change": {"tag": ["tenderUpdate"], "status": None},
    "result": {"tag": ["award", "contract"], "status": "complete"},
    "dir-awa-pre": {"tag": ["award", "contract"], "status": "complete"},
    "cont-modif": {"tag": ["awardUpdate", "contractUpdate"], "status": None},
    # bri type is not mapped as it should be discarded
}


def parse_form_type(
    xml_content: str | bytes,
) -> dict[str, list[str] | dict[str, str]] | None:
    """Parse the form type from XML content and return corresponding OCDS mapping.

    Args:
        xml_content: XML string or bytes containing the notice data

    Returns:
        Dictionary containing 'tag' list and optional 'tender' status mapping,
        or None if parsing fails or should be discarded

    Example:
        >>> result = parse_form_type(xml_string)
        >>> print(result)
        {'tag': ['tender'], 'tender': {'status': 'active'}}

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        namespaces = {
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        }

        notice_type_code = root.xpath(
            "//cbc:NoticeTypeCode[@listName]", namespaces=namespaces
        )

        if not notice_type_code:
            logger.warning("No NoticeTypeCode found in the XML.")
            return None

        list_name = notice_type_code[0].get("listName")

        # Discard notices with form type "bri" as they relate to events
        # outside the lifecycle of a contracting process
        if list_name == "bri":
            logger.info("Discarding notice with form type 'bri'")
            return None

        if list_name not in form_type_mapping:
            logger.warning("Unknown form type: %s", list_name)
            return None

        mapping = form_type_mapping[list_name]

        result = {"tag": mapping["tag"]}

        if mapping["status"] is not None:
            result["tender"] = {"status": mapping["status"]}
    except (etree.XMLSyntaxError, TypeError):
        logger.exception("Error parsing XML content")
        return None
    else:
        return result


def merge_form_type(
    release_json: dict[str, any], form_type_data: dict[str, any] | None
) -> None:
    """Merge form type data into the release JSON.

    Updates the release JSON with form type tags and tender status information.

    Args:
        release_json: The target release JSON document to update
        form_type_data: The form type data containing tags and status to merge

    Example:
        >>> release = {}
        >>> form_data = {'tag': ['tender'], 'tender': {'status': 'active'}}
        >>> merge_form_type(release, form_data)
        >>> print(release)
        {'tag': ['tender'], 'tender': {'status': 'active'}}

    """
    if not form_type_data:
        logger.info("No form type data to merge.")
        return

    release_json["tag"] = form_type_data["tag"]

    if "tender" in form_type_data:
        release_json.setdefault("tender", {}).update(form_type_data["tender"])

    logger.info("Merged form type data: %s", str(form_type_data))
