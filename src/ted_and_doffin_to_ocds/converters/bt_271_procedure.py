# converters/bt_271_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt_271_procedure(xml_content):
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
        "//cac:ProcurementProject/cac:RequestedTenderTotal/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:FrameworkMaximumAmount",
        namespaces=namespaces,
    )

    if amount_element:
        amount_element = amount_element[0]
        amount = float(amount_element.text)
        currency = amount_element.get("currencyID")

        result["tender"] = {
            "techniques": {
                "frameworkAgreement": {
                    "value": {"amount": amount, "currency": currency},
                },
            },
        }

    return result


def merge_bt_271_procedure(release_json, bt_271_procedure_data) -> None:
    if "techniques" in bt_271_procedure_data["tender"]:
        release_json.setdefault("tender", {}).setdefault("techniques", {})[
            "frameworkAgreement"
        ] = bt_271_procedure_data["tender"]["techniques"]["frameworkAgreement"]
        logger.info("Merged BT-271-procedure Framework Maximum Value data")
    else:
        logger.info("No BT-271-procedure Framework Maximum Value data to merge")
