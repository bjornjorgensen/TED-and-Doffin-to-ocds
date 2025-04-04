import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_no_negotiation_necessary(xml_content: str | bytes) -> dict | None:
    """Parse no negotiation necessary information from TED XML.

    Extract information about whether the buyer reserves the right to award the contract
    without negotiation as defined in BT-120 (No Negotiation Necessary).
    Note: TED F02 form indicates this at the procedure level, not per lot.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "secondStage": {
                    "noNegotiationNecessary": true
                }
            }
        }
        Returns None if the indicator is not present.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)

    # Check for the presence of the RIGHT_CONTRACT_INITIAL_TENDERS element in F02 form
    # Its presence indicates the right is reserved (true).
    no_negotiation_path = (
        "//TED_EXPORT/FORM_SECTION/F02_2014/PROCEDURE/RIGHT_CONTRACT_INITIAL_TENDERS"
    )
    no_negotiation_element = root.xpath(no_negotiation_path)

    if no_negotiation_element:
        return {"tender": {"secondStage": {"noNegotiationNecessary": True}}}

    return None


def merge_no_negotiation_necessary(
    release_json: dict, no_negotiation_data: dict | None
) -> None:
    """Merge no negotiation necessary data into the OCDS release.

    Updates the release JSON in-place by adding or updating second stage information
    at the tender level.

    Args:
        release_json: The main OCDS release JSON to be updated.
        no_negotiation_data: The parsed no negotiation data
            in the same format as returned by parse_no_negotiation_necessary().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not no_negotiation_data:
        logger.info("No negotiation necessary data to merge")
        return

    tender = release_json.setdefault("tender", {})
    second_stage = tender.setdefault("secondStage", {})

    if "secondStage" in no_negotiation_data["tender"]:
        second_stage["noNegotiationNecessary"] = no_negotiation_data["tender"][
            "secondStage"
        ]["noNegotiationNecessary"]
        logger.info("Merged no negotiation necessary status at tender level")
