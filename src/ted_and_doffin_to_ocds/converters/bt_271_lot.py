# converters/bt_271_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt_271_lot(xml_content: str | bytes) -> dict | None:
    """Parse framework maximum value from lot-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot information

    Returns:
        Optional[Dict]: Dictionary containing tender lot information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "techniques": {
                            "frameworkAgreement": {
                                "value": {
                                    "amount": float,
                                    "currency": str
                                }
                            }
                        }
                    }
                ]
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath(
            "cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )
        amount_element = lot.xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount",
            namespaces=namespaces,
        )

        if lot_id and amount_element:
            try:
                lot_data = {
                    "id": lot_id[0],
                    "techniques": {
                        "frameworkAgreement": {
                            "value": {
                                "amount": float(amount_element[0].text),
                                "currency": amount_element[0].get("currencyID"),
                            }
                        }
                    },
                }
                result["tender"]["lots"].append(lot_data)
            except (ValueError, IndexError) as e:
                logger.warning(
                    "Error parsing framework maximum value for lot %s: %s", lot_id[0], e
                )

    return result if result["tender"]["lots"] else None


def merge_bt_271_lot(release_json: dict, bt_271_lot_data: dict | None) -> None:
    """Merge framework maximum value data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        bt_271_lot_data (Optional[Dict]): The source data containing tender lots
            to be merged. If None, function returns without making changes.

    """
    if not bt_271_lot_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    for new_lot in bt_271_lot_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {}).setdefault(
                "frameworkAgreement", {}
            )["value"] = new_lot["techniques"]["frameworkAgreement"]["value"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged BT-271-Lot Framework Maximum Value data for %d lots",
        len(bt_271_lot_data["tender"]["lots"]),
    )
