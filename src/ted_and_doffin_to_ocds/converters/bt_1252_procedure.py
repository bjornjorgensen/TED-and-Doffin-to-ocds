# converters/bt_1252_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

RELATIONSHIP_MAPPING = {
    # Maps reason codes to relationship types
    "irregular": "unsuccessfulProcess",
    "unsuitable": "unsuccessfulProcess",
    "additional": "prior",
    "existing": "prior",
    "repetition": "prior",
}


def parse_direct_award_justification(xml_content: str | bytes) -> dict | None:
    """
    Parse BT-1252: Direct award justification identifiers.

    Extracts identifiers of previous procedures that justify direct award,
    mapping reason codes to relationship types.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "relatedProcesses": [
                    {
                        "identifier": str,
                        "scheme": "eu-oj",
                        "relationship": [str]  # from RELATIONSHIP_MAPPING
                    }
                ]
            }
        Returns None if no relevant data found or on error
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"relatedProcesses": []}

        justifications = root.xpath(
            "//cac:TenderingProcess/cac:ProcessJustification"
            "[cbc:ProcessReasonCode/@listName='direct-award-justification']",
            namespaces=NAMESPACES,
        )

        for justification in justifications:
            identifier = justification.xpath(
                "cbc:Description/text()", namespaces=NAMESPACES
            )
            reason_code = justification.xpath(
                "cbc:ProcessReasonCode/text()", namespaces=NAMESPACES
            )

            if identifier:
                process = {
                    "identifier": identifier[0].strip(),
                    "scheme": "eu-oj",
                    "relationship": [],
                }

                if reason_code:
                    relationship = RELATIONSHIP_MAPPING.get(reason_code[0])
                    if relationship:
                        process["relationship"].append(relationship)
                        logger.info(
                            "Added relationship %s for identifier %s",
                            relationship,
                            identifier[0],
                        )

                result["relatedProcesses"].append(process)

        return result if result["relatedProcesses"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing direct award justifications")
        return None


def merge_direct_award_justification(
    release_json: dict, justification_data: dict | None
) -> None:
    """
    Merge direct award justification data into the release JSON.

    Updates or adds related processes with sequential IDs.

    Args:
        release_json: Main OCDS release JSON to update
        justification_data: Direct award justification data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates relatedProcesses array if needed
        - Maintains sequential IDs across all notices
    """
    if not justification_data:
        logger.warning("No direct award justification data to merge")
        return

    related_processes = release_json.setdefault("relatedProcesses", [])

    # Find highest existing ID
    max_id = max((int(p["id"]) for p in related_processes if "id" in p), default=0)

    # Add new processes with sequential IDs
    for process in justification_data["relatedProcesses"]:
        max_id += 1
        process["id"] = str(max_id)
        related_processes.append(process)
        logger.info(
            "Added related process %s with ID %d", process["identifier"], max_id
        )

    logger.info(
        "Merged direct award justification data for %d processes",
        len(justification_data["relatedProcesses"]),
    )
