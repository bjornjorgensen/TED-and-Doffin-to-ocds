import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_title(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse part title from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing tender title with language info,
                                 or None if no valid data is found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {}}

    # Use the exact XPath provided in the specification
    part_title_elements = root.xpath(
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Name",
        namespaces=namespaces,
    )

    if part_title_elements:
        title_element = part_title_elements[0]
        title_text = title_element.text
        language_id = title_element.get("languageID")

        # Store the title text
        result["tender"]["title"] = title_text

        # If language is specified, store it in the result
        if language_id:
            result["tender"]["titleLanguage"] = language_id

    return result if "title" in result["tender"] else None


def merge_part_title(
    release_json: dict[str, Any], part_title_data: dict[str, Any] | None
) -> None:
    """Merge part title data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        part_title_data (Optional[Dict[str, Any]]): Part data containing title to merge

    """
    if not part_title_data:
        return

    # Ensure tender section exists
    tender = release_json.setdefault("tender", {})

    # Merge the title
    tender["title"] = part_title_data["tender"]["title"]

    # Merge the language info if present
    if "titleLanguage" in part_title_data["tender"]:
        tender["titleLanguage"] = part_title_data["tender"]["titleLanguage"]
