# converters/bt_195_bt_540_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt540_lot_unpublished_identifier(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the award criterion description in Lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished identifier data.
        None: If no relevant data is found.
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

    result = {"withheldInformation": []}

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-des']"
    fields_privacy_elements = root.xpath(xpath_query, namespaces=namespaces)

    for fields_privacy in fields_privacy_elements:
        lot_id = fields_privacy.xpath(
            "ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )
        field_identifier = fields_privacy.xpath(
            "efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lot_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_id[0]}",
                "field": "awa-cri-des",
                "name": "Award Criterion Description",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt540_lot_unpublished_identifier(
    release_json,
    unpublished_identifier_data,
):
    """
    Merge the parsed unpublished identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-540)-Lot")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        "Merged unpublished identifier data for BT-195(BT-540)-Lot: %d items",
        len(unpublished_identifier_data["withheldInformation"]),
    )
