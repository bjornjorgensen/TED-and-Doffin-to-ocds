import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Mapping for TED procedure type codes to relationship types
RELATIONSHIP_MAPPING = {
    # Elements indicating unsuccessful processes
    "D_PROC_OPEN": "unsuccessfulProcess",
    "D_PROC_RESTRICTED": "unsuccessfulProcess",
    "D_PROC_COMPETITIVE_DIALOGUE": "unsuccessfulProcess",
    "D_PROC_NEGOTIATED_PRIOR_CALL_COMPETITION": "unsuccessfulProcess",
    # Elements indicating prior processes would map to "prior"
    # Add more mappings as needed
}

# Description mapping for TED procedure types
DESCRIPTION_MAPPING = {
    "D_PROC_OPEN": "No tenders or no suitable tenders/requests to participate in response to open procedure",
    "D_PROC_RESTRICTED": "No tenders or no suitable tenders/requests to participate in response to restricted procedure",
    "D_PROC_COMPETITIVE_DIALOGUE": "No tenders or no suitable tenders/requests to participate in response to competitive dialogue",
    "D_PROC_NEGOTIATED_PRIOR_CALL_COMPETITION": "No tenders or no suitable tenders/requests to participate in response to negotiated procedure with prior publication of a contract notice",
}

# XPath templates for different TED form types
TED_XPATH_TEMPLATES = [
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F03_2014']/*[local-name()='PROCEDURE']/*[local-name()='PT_AWARD_CONTRACT_WITHOUT_CALL']/*[local-name()='D_ACCORDANCE_ARTICLE']/*[local-name()='{}']",
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F15_2014']/*[local-name()='PROCEDURE']/*[local-name()='DIRECTIVE_2014_24_EU']/*[local-name()='PT_NEGOTIATED_WITHOUT_PUBLICATION']/*[local-name()='D_ACCORDANCE_ARTICLE']/*[local-name()='{}']",
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F15_2014']/*[local-name()='PROCEDURE']/*[local-name()='DIRECTIVE_2009_81_EC']/*[local-name()='PT_NEGOTIATED_WITHOUT_PUBLICATION']/*[local-name()='D_ACCORDANCE_ARTICLE']/*[local-name()='{}']",
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F21_2014']/*[local-name()='PROCEDURE']/*[local-name()='PT_AWARD_CONTRACT_WITHOUT_CALL']/*[local-name()='D_ACCORDANCE_ARTICLE']/*[local-name()='{}']",
]

# List of procedure types we're looking for
PROCEDURE_TYPES = [
    "D_PROC_OPEN",
    "D_PROC_RESTRICTED",
    "D_PROC_COMPETITIVE_DIALOGUE",
    "D_PROC_NEGOTIATED_PRIOR_CALL_COMPETITION",
]


def _extract_identifier_from_node(node: etree._Element) -> str | None:
    """Extract the notice identifier from a TED XML node."""
    # Try to get text directly from node
    if node.text and node.text.strip():
        return node.text.strip()
    # If no direct text, try to find notice number in child elements
    if len(node) > 0:
        for child in node:
            if child.tag.endswith("NOTICE_NUMBER_OJ") and child.text:
                return child.text.strip()
    return None


def parse_direct_award_justification(xml_content: str | bytes) -> dict | None:
    """Parse BT-1252: Direct award justification identifiers from TED format.

    Extracts identifiers of previous procedures that justify direct award,
    mapping procedure types to relationship types.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "relatedProcesses": [
                    {
                        "identifier": str,
                        "scheme": "eu-oj",
                        "relationship": [str]
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

        # For each procedure type, check all possible XPath locations
        # These correspond to the TED XPaths listed for BT-1252
        for proc_type in PROCEDURE_TYPES:
            for xpath_template in TED_XPATH_TEMPLATES:
                xpath = xpath_template.format(proc_type)
                nodes = root.xpath(xpath)

                for node in nodes:
                    # Extract the identifier (BT-1252) using the helper function
                    identifier = _extract_identifier_from_node(node)

                    if identifier:
                        process = {
                            "identifier": identifier,  # BT-1252 value
                            "scheme": "eu-oj",
                            "relationship": [],
                        }

                        # Add relationship based on procedure type (maps to OCDS relationship)
                        relationship = RELATIONSHIP_MAPPING.get(proc_type)
                        if relationship:
                            process["relationship"].append(relationship)

                        result["relatedProcesses"].append(process)
                        logger.info(
                            "Found direct award justification with ID %s and relationship %s",
                            identifier,
                            relationship,
                        )

        return result if result["relatedProcesses"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing TED direct award justifications")
        return None


def merge_direct_award_justification(
    release_json: dict, justification_data: dict | None
) -> None:
    """Merge direct award justification data (BT-1252) into the release JSON.

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
        "Merged TED direct award justification data for %d processes",
        len(justification_data["relatedProcesses"]),
    )
