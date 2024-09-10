# converters/BT_23_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_main_nature_procedure(xml_content):
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
        "//cac:ProcurementProject/cbc:ProcurementTypeCode/text()", namespaces=namespaces
    )

    if procurement_type:
        main_category = procurement_type[0]
        if main_category == "supplies":
            main_category = "goods"
        elif main_category not in ["works", "services"]:
            logger.warning(f"Unexpected procurement type: {main_category}")
            return None

        result["tender"]["mainProcurementCategory"] = main_category

    return result if "mainProcurementCategory" in result["tender"] else None


def merge_main_nature_procedure(release_json, main_nature_data):
    if not main_nature_data:
        logger.warning("No Main Nature (Procedure) data to merge")
        return

    if "mainProcurementCategory" in main_nature_data["tender"]:
        release_json.setdefault("tender", {})["mainProcurementCategory"] = (
            main_nature_data["tender"]["mainProcurementCategory"]
        )
        logger.info(
            f"Merged Main Nature (Procedure) data: {main_nature_data['tender']['mainProcurementCategory']}"
        )
    else:
        logger.warning(
            "No mainProcurementCategory found in Main Nature (Procedure) data"
        )
