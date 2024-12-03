import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt_271_lots_group(xml_content: str | bytes) -> dict | None:
    """
    Parse framework maximum value from lot group-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot group information

    Returns:
        Optional[Dict]: Dictionary containing tender lot group information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "lotGroups": [
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

    result = {"tender": {"lotGroups": []}}

    lot_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lot_group in lot_groups:
        group_id = lot_group.xpath(
            "cbc:ID/text()",
            namespaces=namespaces,
        )
        amount_element = lot_group.xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount",
            namespaces=namespaces,
        )

        if group_id and amount_element:
            try:
                group_data = {
                    "id": group_id[0],
                    "techniques": {
                        "frameworkAgreement": {
                            "value": {
                                "amount": float(amount_element[0].text),
                                "currency": amount_element[0].get("currencyID"),
                            }
                        }
                    },
                }
                result["tender"]["lotGroups"].append(group_data)
            except (ValueError, IndexError) as e:
                logger.warning(
                    "Error parsing framework maximum value for lot group %s: %s",
                    group_id[0],
                    e,
                )

    return result if result["tender"]["lotGroups"] else None


def merge_bt_271_lots_group(
    release_json: dict, bt_271_lots_group_data: dict | None
) -> None:
    """
    Merge framework maximum value data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        bt_271_lots_group_data (Optional[Dict]): The source data containing tender lot groups
            to be merged. If None, function returns without making changes.
    """
    if not bt_271_lots_group_data:
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault(
        "lotGroups", []
    )

    for new_group in bt_271_lots_group_data["tender"]["lotGroups"]:
        existing_group = next(
            (g for g in existing_lot_groups if g["id"] == new_group["id"]),
            None,
        )
        if existing_group:
            existing_group.setdefault("techniques", {}).setdefault(
                "frameworkAgreement", {}
            )["value"] = new_group["techniques"]["frameworkAgreement"]["value"]
        else:
            existing_lot_groups.append(new_group)

    logger.info(
        "Merged BT-271-LotsGroup Framework Maximum Value data for %d lot groups",
        len(bt_271_lots_group_data["tender"]["lotGroups"]),
    )
