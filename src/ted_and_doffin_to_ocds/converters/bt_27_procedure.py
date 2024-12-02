# converters/bt_27_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt_27_procedure(xml_content: str | bytes) -> dict[str, Any]:
    """
    Parse the estimated value from procurement project XML content.

    Args:
        xml_content: XML string or bytes containing procurement data

    Returns:
        Dict containing tender value information:
        {
            "tender": {
                "value": {
                    "amount": 250000,
                    "currency": "EUR"
                }
            }
        }
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

    amount_element = root.xpath(
        "//cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount",
        namespaces=namespaces,
    )

    if amount_element:
        amount_element = amount_element[0]
        amount = float(amount_element.text)
        currency = amount_element.get("currencyID")

        result["tender"]["value"] = {"amount": amount, "currency": currency}

    return result


def merge_bt_27_procedure(
    release_json: dict[str, Any], bt_27_procedure_data: dict[str, Any]
) -> None:
    """
    Merge estimated value data into existing release JSON.

    Args:
        release_json: Target release JSON to merge into
        bt_27_procedure_data: Source data containing tender value information

    Returns:
        None. Modifies release_json in place.
        Logs success or absence of data to merge.
    """
    if "value" in bt_27_procedure_data["tender"]:
        release_json.setdefault("tender", {})["value"] = bt_27_procedure_data["tender"][
            "value"
        ]
        logger.info("Merged BT-27-procedure Estimated Value data")
    else:
        logger.info("No BT-27-procedure Estimated Value data to merge")
