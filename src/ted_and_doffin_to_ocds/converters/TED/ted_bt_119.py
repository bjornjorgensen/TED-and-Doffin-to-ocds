import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_dps_termination(xml_content: str | bytes) -> dict | None:
    """Parse dynamic purchasing system termination information from TED XML.

    Extract information about whether the dynamic purchasing system is terminated
    as defined in BT-119 (Dynamic Purchasing System Termination).
    Note: TED F03 form indicates termination at the procedure level, not per lot.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "techniques": {
                    "dynamicPurchasingSystem": {
                        "status": "terminated"
                    }
                }
            }
        }
        Returns None if no relevant data is found or DPS is not terminated.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    # Check for DPS termination in F03 form
    termination_path = (
        "//TED_EXPORT/FORM_SECTION/F03_2014/PROCEDURE/TERMINATION_DPS/text()"
    )
    termination_status = root.xpath(termination_path)

    if termination_status and termination_status[0].upper() == "YES":
        return {
            "tender": {
                "techniques": {"dynamicPurchasingSystem": {"status": "terminated"}}
            }
        }

    return None


def merge_dps_termination(
    release_json: dict, dps_termination_data: dict | None
) -> None:
    """Merge DPS termination data into the OCDS release.

    Updates the release JSON in-place by adding or updating dynamic purchasing system
    information at the tender level.

    Args:
        release_json: The main OCDS release JSON to be updated.
        dps_termination_data: The parsed DPS termination data
            in the same format as returned by parse_dps_termination().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not dps_termination_data:
        logger.info("No DPS termination data to merge")
        return

    tender = release_json.setdefault("tender", {})
    techniques = tender.setdefault("techniques", {})

    if "dynamicPurchasingSystem" in dps_termination_data["tender"]["techniques"]:
        dps_info = techniques.setdefault("dynamicPurchasingSystem", {})
        dps_info["status"] = dps_termination_data["tender"]["techniques"][
            "dynamicPurchasingSystem"
        ]["status"]
        logger.info("Merged DPS termination status at tender level")
