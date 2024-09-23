# converters/bt_24_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_description(xml_content):
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

    result = {"tender": {}}

    description = root.xpath(
        "//cac:ProcurementProject/cbc:Description/text()",
        namespaces=namespaces,
    )

    if description:
        result["tender"]["description"] = description[0]
        return result

    return None


def merge_procedure_description(release_json, procedure_description_data):
    if not procedure_description_data:
        logger.warning("No procedure Description data to merge")
        return

    release_json.setdefault("tender", {})["description"] = procedure_description_data[
        "tender"
    ]["description"]
    logger.info("Merged procedure Description data")
