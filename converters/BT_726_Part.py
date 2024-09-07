# converters/BT_726_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_sme_suitability(xml_content):
    """
    Parse the XML content to extract SME suitability information for the procurement part.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed SME suitability data for the procurement part.
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

    sme_suitable = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:SMESuitableIndicator/text()",
        namespaces=namespaces,
    )

    if sme_suitable:
        return {"tender": {"suitability": {"sme": sme_suitable[0].lower() == "true"}}}

    return None


def merge_part_sme_suitability(release_json, part_sme_suitability_data):
    """
    Merge the parsed SME suitability data for the procurement part into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        part_sme_suitability_data (dict): The parsed SME suitability data for the procurement part to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not part_sme_suitability_data:
        logger.warning("No procurement part SME suitability data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "suitability" not in release_json["tender"]:
        release_json["tender"]["suitability"] = {}

    release_json["tender"]["suitability"]["sme"] = part_sme_suitability_data["tender"][
        "suitability"
    ]["sme"]

    logger.info("Merged SME suitability data for procurement part")
