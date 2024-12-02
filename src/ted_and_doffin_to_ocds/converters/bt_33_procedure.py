# converters/bt_33_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_max_lots_awarded(xml_content: str | bytes) -> dict | None:
    """
    Parse the maximum number of lots that can be awarded to one tenderer from XML content.

    Args:
        xml_content (str | bytes): The XML content containing lot distribution information.

    Returns:
        dict | None: A dictionary containing the maximum lots awarded per supplier in OCDS format,
                    or None if the information is not found or invalid.
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

    max_lots_awarded = root.xpath(
        "//cac:LotDistribution/cbc:MaximumLotsAwardedNumeric/text()",
        namespaces=namespaces,
    )

    if max_lots_awarded:
        try:
            return {
                "tender": {
                    "lotDetails": {
                        "maximumLotsAwardedPerSupplier": int(max_lots_awarded[0]),
                    },
                },
            }
        except ValueError:
            logger.warning(
                "Invalid MaximumLotsAwardedNumeric value: %s", max_lots_awarded[0]
            )

    return None


def merge_max_lots_awarded(
    release_json: dict, max_lots_awarded_data: dict | None
) -> None:
    """
    Merge the maximum lots awarded data into the release JSON.

    Args:
        release_json (dict): The target release JSON to merge into.
        max_lots_awarded_data (dict | None): The maximum lots awarded data to merge,
                                           or None if no data to merge.

    Returns:
        None
    """
    if not max_lots_awarded_data:
        return

    release_json.setdefault("tender", {}).setdefault("lotDetails", {}).update(
        max_lots_awarded_data["tender"]["lotDetails"],
    )
    logger.info("Merged Maximum Lots Awarded data")
