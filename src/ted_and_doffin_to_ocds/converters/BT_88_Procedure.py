# converters/BT_88_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_features(xml_content):
    """
    Parse the XML content to extract the procedure features.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed procedure features.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    procedure_features = root.xpath(
        "//cac:TenderingProcess/cbc:Description/text()", namespaces=namespaces,
    )

    if procedure_features:
        return {"tender": {"procurementMethodDetails": procedure_features[0]}}

    return None


def merge_procedure_features(release_json, procedure_features_data):
    """
    Merge the parsed procedure features data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        procedure_features_data (dict): The parsed procedure features data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not procedure_features_data:
        logger.warning("No procedure features data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender["procurementMethodDetails"] = procedure_features_data["tender"][
        "procurementMethodDetails"
    ]

    logger.info("Merged procedure features data")
