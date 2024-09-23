# converters/BT_23_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_main_nature_part(xml_content):
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

    procurement_type = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()",
        namespaces=namespaces,
    )

    if procurement_type:
        main_category = procurement_type[0]
        if main_category == "supplies":
            main_category = "goods"

        result["tender"]["mainProcurementCategory"] = main_category

    return result if "mainProcurementCategory" in result["tender"] else None


def merge_main_nature_part(release_json, main_nature_data):
    if not main_nature_data:
        logger.warning("No Main Nature (Part) data to merge")
        return

    if "mainProcurementCategory" in main_nature_data["tender"]:
        release_json.setdefault("tender", {})["mainProcurementCategory"] = (
            main_nature_data["tender"]["mainProcurementCategory"]
        )
        logger.info(
            f"Merged Main Nature (Part) data: {main_nature_data['tender']['mainProcurementCategory']}",
        )
    else:
        logger.warning("No mainProcurementCategory found in Main Nature (Part) data")
