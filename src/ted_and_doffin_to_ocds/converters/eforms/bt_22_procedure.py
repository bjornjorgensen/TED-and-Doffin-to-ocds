import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_internal_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse internal identifier from procedure XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing tender identifier data,
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

    internal_id = root.xpath(
        "/*/cac:ProcurementProject/cbc:ID[@schemeName='InternalID']/text()",
        namespaces=namespaces,
    )

    if internal_id:
        return {
            "tender": {"identifiers": [{"id": internal_id[0], "scheme": "internal"}]}
        }

    return None


def merge_procedure_internal_identifier(
    release_json: dict[str, Any],
    procedure_internal_identifier_data: dict[str, Any] | None,
) -> None:
    """Merge procedure internal identifier data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        procedure_internal_identifier_data (Optional[Dict[str, Any]]): Tender identifier data to merge

    """
    if not procedure_internal_identifier_data:
        logger.warning("No procedure internal identifier data to merge")
        return

    release_json.setdefault("tender", {})["identifiers"] = (
        procedure_internal_identifier_data["tender"]["identifiers"]
    )
