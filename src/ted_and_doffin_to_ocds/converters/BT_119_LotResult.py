# converters/BT_119_LotResult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_dps_termination(xml_content):
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

    result = {"lots": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces,
    )

    for lot_result in lot_results:
        dps_termination = lot_result.xpath(
            "efbc:DPSTerminationIndicator/text()", namespaces=namespaces,
        )
        if dps_termination and dps_termination[0].lower() == "true":
            lot_id = lot_result.xpath(
                "../efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                namespaces=namespaces,
            )
            if lot_id:
                result["lots"].append(
                    {
                        "id": lot_id[0],
                        "techniques": {
                            "dynamicPurchasingSystem": {"status": "terminated"},
                        },
                    },
                )

    return result if result["lots"] else None


def merge_dps_termination(release_json, dps_termination_data):
    if not dps_termination_data:
        logger.warning("No DPS Termination data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in dps_termination_data["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {})["dynamicPurchasingSystem"] = (
                new_lot["techniques"]["dynamicPurchasingSystem"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged DPS Termination data for {len(dps_termination_data['lots'])} lots",
    )
