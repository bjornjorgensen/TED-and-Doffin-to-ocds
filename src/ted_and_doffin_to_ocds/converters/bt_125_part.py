# converters/bt_125_part.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_previous_planning_identifier_part(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the previous planning identifier information from part-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing part information

    Returns:
        Optional[Dict]: Dictionary containing related processes information, or None if no data found
        The structure follows the format:
        {
            "relatedProcesses": [
                {
                    "id": str,
                    "relationship": ["planning"],
                    "scheme": "eu-oj",
                    "identifier": str  # Concatenated identifier with part ID
                }
            ]
        }

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
    related_process_id = 1

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
        namespaces=namespaces,
    )

    for part in parts:
        notice_refs = part.xpath(
            "cac:TenderingProcess/cac:NoticeDocumentReference",
            namespaces=namespaces,
        )

        for notice_ref in notice_refs:
            identifier = notice_ref.xpath(
                "cbc:ID[@schemeName='notice-id-ref']/text()",
                namespaces=namespaces,
            )
            part_identifier = notice_ref.xpath(
                "cbc:ReferencedDocumentInternalAddress/text()",
                namespaces=namespaces,
            )

            if identifier and part_identifier:
                full_identifier = f"{identifier[0]}-{part_identifier[0]}"
                related_process = {
                    "id": str(related_process_id),
                    "relationship": ["planning"],
                    "scheme": "eu-oj",
                    "identifier": full_identifier,
                }
                result["relatedProcesses"].append(related_process)
                related_process_id += 1

    return result if result["relatedProcesses"] else None


def merge_previous_planning_identifier_part(
    release_json: dict, previous_planning_data: dict | None
) -> None:
    """Merge previous planning identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        previous_planning_data (Optional[Dict]): The source data containing related processes
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        relatedProcesses field with new planning identifiers.

    """
    if not previous_planning_data:
        logger.warning("No Previous Planning Identifier (Part) data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])

    for new_process in previous_planning_data["relatedProcesses"]:
        existing_process = next(
            (
                p
                for p in existing_related_processes
                if p["identifier"] == new_process["identifier"]
            ),
            None,
        )
        if existing_process:
            existing_process.update(new_process)
        else:
            existing_related_processes.append(new_process)

    logger.info(
        "Merged Previous Planning Identifier (Part) data for %d related processes",
        len(previous_planning_data["relatedProcesses"]),
    )
