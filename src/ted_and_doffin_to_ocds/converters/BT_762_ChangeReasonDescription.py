# converters/BT_762_ChangeReasonDescription.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_change_reason_description(xml_content: str) -> list[dict[str, str]] | None:
    """
    Parse the XML content to extract the change reason description.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[List[Dict[str, str]]]: A list of dictionaries containing the parsed change reason descriptions.
                                        Each dictionary has a 'rationale' key with the description as its value.
                                        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
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

    change_reasons = root.xpath(
        "//efac:Changes/efac:ChangeReason/efbc:ReasonDescription/text()",
        namespaces=namespaces,
    )

    if change_reasons:
        return [{"rationale": reason.strip()} for reason in change_reasons]
    return None


def merge_change_reason_description(
    release_json: dict, change_reason_data: list[dict[str, str]],
) -> None:
    """
    Merge the parsed change reason description data into the main OCDS release JSON.

    This function updates the existing amendments in the release JSON with the
    change reason descriptions. If no amendments exist, it creates new ones.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        change_reason_data (List[Dict[str, str]]): The parsed change reason description data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not change_reason_data:
        logger.warning("No Change Reason Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    amendments = tender.setdefault("amendments", [])

    for index, reason in enumerate(change_reason_data):
        if index < len(amendments):
            amendments[index].update(reason)
        else:
            amendments.append(reason)

    logger.info(
        f"Merged Change Reason Description data for {len(change_reason_data)} amendments",
    )
