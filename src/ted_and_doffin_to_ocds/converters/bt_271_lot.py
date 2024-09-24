# converters/bt_271_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_bt_271_lot(xml_content):
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

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)
        amount_element = lot_element.xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount",
            namespaces=namespaces,
        )

        if lot_id and amount_element:
            lot_id = lot_id[0]
            amount_element = amount_element[0]
            amount = float(amount_element.text)
            currency = amount_element.get("currencyID")

            lot = {
                "id": lot_id,
                "techniques": {
                    "frameworkAgreement": {
                        "value": {"amount": amount, "currency": currency},
                    },
                },
            }

            result["tender"]["lots"].append(lot)

    return result


def merge_bt_271_lot(release_json, bt_271_lot_data):
    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in bt_271_lot_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {}).setdefault(
                "frameworkAgreement",
                {},
            )["value"] = new_lot["techniques"]["frameworkAgreement"]["value"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged BT-271-Lot Framework Maximum Value data for %d lots",
        len(bt_271_lot_data["tender"]["lots"]),
    )
