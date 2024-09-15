# converters/BT_195_BT_541_LotsGroup_Fixed.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the LotsGroup fixed award criterion.

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

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']"
    lots_groups = root.xpath(xpath_query, namespaces=namespaces)

    for lots_group in lots_groups:
        lots_group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        field_identifier = lots_group.xpath(
            ".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-num']/efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-fixed-{lots_group_id}",
                "field": "awa-cri-num",
                "name": "Award Criterion Number Fixed",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier(
    release_json, unpublished_identifier_data
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
        logger.warning(
            "No unpublished identifier data to merge for BT-195(BT-541) LotsGroup Fixed"
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        f"Merged unpublished identifier data for BT-195(BT-541) LotsGroup Fixed for {len(unpublished_identifier_data['withheldInformation'])} lots groups"
    )
