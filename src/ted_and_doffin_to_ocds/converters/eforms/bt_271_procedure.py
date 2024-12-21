# converters/bt_271_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt_271_procedure(xml_content: str | bytes) -> dict | None:
    """Parse framework maximum value from procedure-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing procedure information

    Returns:
        Optional[Dict]: Dictionary containing tender information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "techniques": {
                    "frameworkAgreement": {
                        "value": {
                            "amount": float,
                            "currency": str
                        }
                    }
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

    amount_element = root.xpath(
        "/*/cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount",
        namespaces=namespaces,
    )

    if amount_element:
        try:
            return {
                "tender": {
                    "techniques": {
                        "frameworkAgreement": {
                            "value": {
                                "amount": float(amount_element[0].text),
                                "currency": amount_element[0].get("currencyID"),
                            }
                        }
                    }
                }
            }
        except (ValueError, IndexError) as e:
            logger.warning("Error parsing framework maximum value: %s", e)

    return None


def merge_bt_271_procedure(
    release_json: dict, bt_271_procedure_data: dict | None
) -> None:
    """Merge framework maximum value data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        bt_271_procedure_data (Optional[Dict]): The source data containing tender
            to be merged. If None, function returns without making changes.

    """
    if not bt_271_procedure_data:
        return

    if "techniques" in bt_271_procedure_data.get("tender", {}):
        release_json.setdefault("tender", {}).setdefault("techniques", {})[
            "frameworkAgreement"
        ] = bt_271_procedure_data["tender"]["techniques"]["frameworkAgreement"]
