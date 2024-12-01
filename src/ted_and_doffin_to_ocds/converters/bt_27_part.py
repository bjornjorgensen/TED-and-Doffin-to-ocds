# converters/bt_27_part.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt_27_part(xml_content: str | bytes) -> dict:
    """Parse BT-27 estimated value from the procurement project lot XML.

    Args:
        xml_content (Union[str, bytes]): XML content containing procurement data

    Returns:
        Dict: Dictionary containing tender value information in OCDS format with
            amount and currency if found, otherwise empty tender dict
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

    result = {"tender": {}}

    part_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
        namespaces=namespaces,
    )

    if part_elements:
        amount_element = part_elements[0].xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount",
            namespaces=namespaces,
        )

        if amount_element:
            amount_element = amount_element[0]
            amount = float(amount_element.text)
            currency = amount_element.get("currencyID")

            result["tender"]["value"] = {"amount": amount, "currency": currency}

    return result


def merge_bt_27_part(release_json: dict, bt_27_part_data: dict) -> None:
    """Merge BT-27 estimated value data into the release JSON.

    Args:
        release_json (Dict): Target release JSON to merge data into
        bt_27_part_data (Dict): Source data containing tender value information

    Returns:
        None: Modifies release_json in place
    """
    if "value" in bt_27_part_data["tender"]:
        release_json.setdefault("tender", {})["value"] = bt_27_part_data["tender"][
            "value"
        ]
        logger.info("Merged BT-27-part Estimated Value data")
    else:
        logger.info("No BT-27-part Estimated Value data to merge")
