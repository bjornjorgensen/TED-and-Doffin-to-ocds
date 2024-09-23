# converters/OPP_040_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_main_nature_sub_type(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

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

    result = {"tender": {"additionalProcurementCategories": []}}

    additional_types = root.xpath(
        "//cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='transport-service']/cbc:ProcurementTypeCode/text()",
        namespaces=namespaces,
    )

    if additional_types:
        result["tender"]["additionalProcurementCategories"] = additional_types

    return result if result["tender"]["additionalProcurementCategories"] else None


def merge_main_nature_sub_type(release_json, main_nature_sub_type_data):
    if not main_nature_sub_type_data:
        logger.warning("No Main Nature - Sub Type data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_categories = tender.setdefault("additionalProcurementCategories", [])

    new_categories = main_nature_sub_type_data["tender"][
        "additionalProcurementCategories"
    ]
    for category in new_categories:
        if category not in existing_categories:
            existing_categories.append(category)

    logger.info(
        f"Merged Main Nature - Sub Type: added {len(new_categories)} categories",
    )
