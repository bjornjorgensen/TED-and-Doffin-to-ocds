# converters/bt_31_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_max_lots_allowed(xml_content):
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

    max_lots_element = root.xpath(
        "//cac:TenderingTerms/cac:LotDistribution/cbc:MaximumLotsSubmittedNumeric",
        namespaces=namespaces,
    )

    if max_lots_element:
        max_lots = int(max_lots_element[0].text)
        return {"tender": {"lotDetails": {"maximumLotsBidPerSupplier": max_lots}}}

    return None


def merge_max_lots_allowed(release_json, max_lots_data):
    if not max_lots_data:
        logger.warning("No Maximum Lots Allowed data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lot_details = tender.setdefault("lotDetails", {})
    lot_details.update(max_lots_data["tender"]["lotDetails"])

    logger.info(
        f"Merged Maximum Lots Allowed data: {max_lots_data['tender']['lotDetails']['maximumLotsBidPerSupplier']}",
    )
