import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_previous_planning_identifier_lot(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the previous planning identifier information from TED XML data.

    Extract information about previous planning notice identifiers from TED XML format
    for BT-125 at the lot level.

    Args:
        xml_content (Union[str, bytes]): The TED XML content to parse

    Returns:
        Optional[Dict]: Dictionary containing related processes information, or None if no data found
        The structure follows the format:
        {
            "relatedProcesses": [
                {
                    "id": str,
                    "relationship": ["planning"],
                    "scheme": "eu-notice-id-ref",
                    "identifier": str
                }
            ]
        }

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    # TED XML paths for different form types based on BT-125(i)-Lot metadata
    form_paths = [
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='CONTRACT_DEFENCE']/*[local-name()='FD_CONTRACT_DEFENCE']/*[local-name()='PROCEDURE_DEFINITION_CONTRACT_NOTICE_DEFENCE']/*[local-name()='ADMINISTRATIVE_INFORMATION_CONTRACT_NOTICE_DEFENCE']/*[local-name()='PREVIOUS_PUBLICATION_INFORMATION_NOTICE_F17']/*[local-name()='PREVIOUS_PUBLICATION_EXISTS_F17']/*[local-name()='PREVIOUS_PUBLICATION_NOTICE_F17']/*[local-name()='NOTICE_NUMBER_OJ']",
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F21_2014']/*[local-name()='PROCEDURE']/*[local-name()='NOTICE_NUMBER_OJ']",
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F22_2014']/*[local-name()='PROCEDURE']/*[local-name()='NOTICE_NUMBER_OJ']",
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F23_2014']/*[local-name()='PROCEDURE']/*[local-name()='NOTICE_NUMBER_OJ']",
        "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F25_2014']/*[local-name()='PROCEDURE']/*[local-name()='NOTICE_NUMBER_OJ']",
    ]

    result = {"relatedProcesses": []}
    related_process_id = 1

    for path in form_paths:
        notice_nodes = root.xpath(path)

        for notice in notice_nodes:
            if notice.text and notice.text.strip():
                # Pattern validation could be added here if needed
                # Pattern: ^([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}-(0[1-9]|[1-9]\d)|(\d{1,8})-(19|20)\d\d)$

                related_process = {
                    "id": str(related_process_id),
                    "relationship": ["planning"],
                    "scheme": "eu-notice-id-ref",
                    "identifier": notice.text.strip(),
                }

                result["relatedProcesses"].append(related_process)
                related_process_id += 1

    return result if result["relatedProcesses"] else None


def merge_previous_planning_identifier_lot(
    release_json: dict, previous_planning_data: dict | None
) -> None:
    """Merge previous planning identifier data from TED format into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        previous_planning_data (Optional[Dict]): The source data containing related processes
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        relatedProcesses field with new planning identifiers.
    """
    if not previous_planning_data:
        logger.warning("No Previous Planning Identifier (Lot) data to merge")
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
        if not existing_process:
            existing_related_processes.append(new_process)

    logger.info(
        "Merged Previous Planning Identifier (Lot) data for %d related processes",
        len(previous_planning_data["relatedProcesses"]),
    )
