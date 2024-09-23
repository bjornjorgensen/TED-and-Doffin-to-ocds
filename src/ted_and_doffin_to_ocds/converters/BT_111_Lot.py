# converters/BT_111_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_framework_buyer_categories(xml_content):
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        buyer_categories = lot.xpath(
            ".//cac:TenderingProcess/cac:FrameworkAgreement/cac:SubsequentProcessTenderRequirement[cbc:Name/text()='buyer-categories']/cbc:Description/text()",
            namespaces=namespaces,
        )

        if buyer_categories:
            lot_data = {
                "id": lot_id,
                "techniques": {
                    "frameworkAgreement": {"buyerCategories": buyer_categories[0]},
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_framework_buyer_categories(release_json, framework_buyer_categories_data):
    if not framework_buyer_categories_data:
        logger.warning("No Framework Buyer Categories data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in framework_buyer_categories_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {}).setdefault(
                "frameworkAgreement", {},
            ).update(new_lot["techniques"]["frameworkAgreement"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged Framework Buyer Categories data for {len(framework_buyer_categories_data['tender']['lots'])} lots",
    )
