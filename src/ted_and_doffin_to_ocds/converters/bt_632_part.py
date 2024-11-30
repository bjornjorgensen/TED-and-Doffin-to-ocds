# converters/bt_632_part.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tool_name_part(xml_content):
    """
    Parse the XML content to extract the tool name for electronic communication for the part.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed tool name in the format:
              {
                  "tender": {
                      "communication": {
                          "atypicalToolName": "tool_name"
                      }
                  }
              }
        None: If no relevant data is found.
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

    tool_name = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:AccessToolName/text()",
        namespaces=namespaces,
    )

    if tool_name:
        return {"tender": {"communication": {"atypicalToolName": tool_name[0]}}}

    return None


def merge_tool_name_part(release_json, tool_name_data) -> None:
    """
    Merge the parsed tool name data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        tool_name_data (dict): The parsed tool name data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not tool_name_data:
        logger.warning("No tool name data to merge for part")
        return

    release_json.setdefault("tender", {}).setdefault("communication", {}).update(
        tool_name_data["tender"]["communication"],
    )

    logger.info("Merged tool name data for part")
