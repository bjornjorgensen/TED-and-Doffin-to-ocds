# converters/bt_195_bt_734_lotsgroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt734_lotsgroup_unpublished_identifier(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the award criterion name in lot groups.

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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    xpath_query = (
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']"
        "/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion"
        "/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension"
        "/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy"
        "[efbc:FieldIdentifierCode/text()='awa-cri-nam']"
    )

    for field_privacy in root.xpath(xpath_query, namespaces=namespaces):
        lot_group_id = field_privacy.xpath(
            "ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='LotsGroup']/text()",
            namespaces=namespaces,
        )
        field_identifier = field_privacy.xpath(
            "efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lot_group_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_group_id[0]}",
                "field": "awa-cri-nam",
                "name": "Award Criterion Name",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt734_lotsgroup_unpublished_identifier(
    release_json,
    unpublished_identifier_data,
) -> None:
    """
    Merge the parsed unpublished identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning(
            "No unpublished identifier data to merge for BT-195(BT-734)-LotsGroup",
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_identifier_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item.update(new_item)
        else:
            withheld_info.append(new_item)

    logger.info(
        "Merged unpublished identifier data for BT-195(BT-734)-LotsGroup: %d items",
        len(unpublished_identifier_data["withheldInformation"]),
    )
