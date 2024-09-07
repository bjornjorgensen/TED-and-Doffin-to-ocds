# converters/BT_33_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_max_lots_awarded(xml_content):
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

    max_lots_awarded = root.xpath(
        "//cac:LotDistribution/cbc:MaximumLotsAwardedNumeric/text()",
        namespaces=namespaces,
    )

    if max_lots_awarded:
        try:
            return {
                "tender": {
                    "lotDetails": {
                        "maximumLotsAwardedPerSupplier": int(max_lots_awarded[0])
                    }
                }
            }
        except ValueError:
            logger.warning(
                f"Invalid MaximumLotsAwardedNumeric value: {max_lots_awarded[0]}"
            )

    return None


def merge_max_lots_awarded(release_json, max_lots_awarded_data):
    if not max_lots_awarded_data:
        return

    release_json.setdefault("tender", {}).setdefault("lotDetails", {}).update(
        max_lots_awarded_data["tender"]["lotDetails"]
    )
    logger.info("Merged Maximum Lots Awarded data")
