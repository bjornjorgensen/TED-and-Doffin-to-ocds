# converters/bt_03.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

form_type_mapping = {
    "planning": {"tag": ["tender"], "status": "planned"},
    "competition": {"tag": ["tender"], "status": "active"},
    "change": {"tag": ["tenderUpdate"], "status": None},
    "result": {"tag": ["award", "contract"], "status": "complete"},
    "dir-awa-pre": {"tag": ["award", "contract"], "status": "complete"},
    "cont-modif": {"tag": ["awardUpdate", "contractUpdate"], "status": None},
}


def parse_form_type(xml_content: str | bytes) -> dict | None:
    """Parse the form type from XML content and return corresponding OCDS mapping.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing tag and tender status information, or None if parsing fails
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


def merge_form_type(release_json: dict, form_type_data: dict | None) -> None:
    """Merge form type data into the release JSON.

    Args:
        release_json: The release JSON to update
        form_type_data: The form type data to merge

    Returns:
        None
    """
    if not form_type_data:
        logger.info("No form type data to merge.")
        return

    release_json["tag"] = form_type_data["tag"]

    if "tender" in form_type_data:
        release_json.setdefault("tender", {}).update(form_type_data["tender"])

    logger.info("Merged form type data: %s", str(form_type_data))
