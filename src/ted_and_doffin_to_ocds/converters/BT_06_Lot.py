# converters/BT_06_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_strategic_procurement(xml_content):
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

    strategic_procurement_mapping = {
        "env-imp": "environmental",
        "inn-pur": "economic.innovativePurchase",
        "none": "none",
        "soc-obj": "social",
    }

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        procurement_types = lot.xpath(
            ".//cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='strategic-procurement']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces,
        )

        lot_data = {"id": lot_id, "hasSustainability": False, "sustainability": []}

        for procurement_type in procurement_types:
            if procurement_type != "none":
                lot_data["hasSustainability"] = True
                sustainability = {
                    "goal": strategic_procurement_mapping.get(procurement_type, ""),
                    "strategies": [
                        "awardCriteria",
                        "contractPerformanceConditions",
                        "selectionCriteria",
                        "technicalSpecifications",
                    ],
                }
                lot_data["sustainability"].append(sustainability)

        if lot_data["hasSustainability"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_strategic_procurement(release_json, strategic_procurement_data):
    if not strategic_procurement_data:
        logger.warning("No Strategic Procurement data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in strategic_procurement_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot["hasSustainability"] = new_lot["hasSustainability"]
            existing_lot["sustainability"] = new_lot["sustainability"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged Strategic Procurement data for {len(strategic_procurement_data['tender']['lots'])} lots",
    )
