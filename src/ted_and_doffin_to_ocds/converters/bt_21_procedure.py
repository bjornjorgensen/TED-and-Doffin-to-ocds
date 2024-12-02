import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_title(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse procedure title from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing tender title,
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

    procedure_title = root.xpath(
        "/*/cac:ProcurementProject/cbc:Name/text()",
        namespaces=namespaces,
    )

    if procedure_title:
        result["tender"]["title"] = procedure_title[0]

    return result if "title" in result["tender"] else None


def merge_procedure_title(
    release_json: dict[str, Any], procedure_title_data: dict[str, Any] | None
) -> None:
    """Merge procedure title data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        procedure_title_data (Optional[Dict[str, Any]]): Tender data containing title to merge
    """
    if not procedure_title_data:
        return

    release_json.setdefault("tender", {})["title"] = procedure_title_data["tender"][
        "title"
    ]
