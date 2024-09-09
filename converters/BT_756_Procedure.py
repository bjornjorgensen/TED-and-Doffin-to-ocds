# converters/BT_756_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_pin_competition_termination(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the PIN competition termination information.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data, or None if no relevant data is found.
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

    terminated_indicator = root.xpath(
        "//cac:TenderingProcess/cbc:TerminatedIndicator/text()", namespaces=namespaces
    )

    if terminated_indicator and terminated_indicator[0].lower() == "true":
        return {"tender": {"status": "complete"}}

    return None


def merge_pin_competition_termination(
    release_json: dict, parsed_data: dict | None
) -> None:
    """
    Merge the parsed PIN competition termination data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        parsed_data (Optional[Dict]): The parsed PIN competition termination data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not parsed_data:
        logger.info("No PIN Competition Termination data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender["status"] = parsed_data["tender"]["status"]

    logger.info("Merged PIN Competition Termination data")
