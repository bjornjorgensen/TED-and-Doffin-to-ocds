# converters/bt_196_bt_541_Lot_fixed.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt196_bt541_lot_fixed_unpublished_justification(xml_content):
    """
    Parse the XML content to extract the unpublished justification description for the award criterion number fixed in Lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished justification data.
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

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-num']"
    fields_privacy_elements = root.xpath(xpath_query, namespaces=namespaces)

    for fields_privacy in fields_privacy_elements:
        lot_id = fields_privacy.xpath(
            "ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )
        reason_description = fields_privacy.xpath(
            "efbc:ReasonDescription/text()",
            namespaces=namespaces,
        )

        if lot_id and reason_description:
            withheld_info = {
                "id": f"awa-cri-num-fixed-{lot_id[0]}",
                "field": "awa-cri-num",
                "rationale": reason_description[0],
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt196_bt541_lot_fixed_unpublished_justification(
    release_json,
    unpublished_justification_data,
):
    """
    Merge the parsed unpublished justification data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_justification_data (dict): The parsed unpublished justification data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_justification_data:
        logger.warning(
            "No unpublished justification data to merge for BT-196(BT-541)-Lot-Fixed",
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_justification_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item["rationale"] = new_item["rationale"]
        else:
            withheld_info.append(new_item)

    logger.info(
        f"Merged unpublished justification data for BT-196(BT-541)-Lot-Fixed: {len(unpublished_justification_data['withheldInformation'])} items",
    )
