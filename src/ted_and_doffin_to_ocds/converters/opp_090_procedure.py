# converters/OPP_090_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_previous_notice_identifier(
    xml_content: str | bytes,
) -> dict[str, list] | None:
    """Parse previous notice identifier from XML content.

    Args:
        xml_content (str | bytes): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, list]]: Dictionary containing related processes information,
        or None if no related processes found
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

    result = {"relatedProcesses": []}
    notice_refs = root.xpath(
        "//cac:TenderingProcess/cac:NoticeDocumentReference/cbc:ID[@schemeName='notice-id-ref']/text()",
        namespaces=namespaces,
    )

    for identifier in notice_refs:
        related_process = {
            "id": str(len(result["relatedProcesses"]) + 1),
            "relationship": ["planning"],
            "scheme": "eu-oj",
            "identifier": identifier,
        }
        result["relatedProcesses"].append(related_process)

    return result if result["relatedProcesses"] else None


def merge_previous_notice_identifier(
    release_json: dict[str, Any], previous_notice_data: dict[str, list] | None
) -> None:
    """Merge previous notice identifier data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        previous_notice_data (Optional[Dict[str, list]]): Previous notice data to merge

    Returns:
        None: Updates release_json in place
    """
    if not previous_notice_data:
        logger.warning("No Previous notice Identifier data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])

    for new_process in previous_notice_data["relatedProcesses"]:
        existing_process = next(
            (
                p
                for p in existing_related_processes
                if p["identifier"] == new_process["identifier"]
            ),
            None,
        )
        if existing_process:
            # Update the existing process if needed
            existing_process["relationship"] = list(
                set(existing_process["relationship"] + new_process["relationship"])
            )
        else:
            # New process id is handled during parse_previous_notice_identifier
            existing_related_processes.append(new_process)

    logger.info(
        "Merged Previous notice Identifier for %d related processes",
        len(previous_notice_data["relatedProcesses"]),
    )
    logger.info("Updated relatedProcesses: %s", existing_related_processes)
