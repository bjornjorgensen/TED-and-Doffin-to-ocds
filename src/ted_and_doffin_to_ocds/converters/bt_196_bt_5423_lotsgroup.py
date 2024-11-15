# converters/bt_196_bt_5423_lotsgroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt196_bt5423_lotsgroup(xml_content):
    """
    Parse the XML content to extract the unpublished justification description for the lots group.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished justification description data.
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

    xpath_query = (
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']"
        "/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion"
        "/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension"
        "/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter"
        "[efbc:ParameterCode/@listName='number-threshold']"
        "/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-thr']"
        "/efbc:ReasonDescription"
    )

    reason_descriptions = root.xpath(xpath_query, namespaces=namespaces)

    for description in reason_descriptions:
        withheld_info = {"field": "awa-cri-thr", "rationale": description.text}
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt196_bt5423_lotsgroup(release_json, unpublished_justification_data):
    """
    Merge the parsed unpublished justification description data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_justification_data (dict): The parsed unpublished justification description data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_justification_data:
        logger.warning(
            "No unpublished justification description data to merge for BT-196(BT-5423)-LotsGroup",
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_justification_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("field") == new_item["field"]),
            None,
        )
        if existing_item:
            existing_item["rationale"] = new_item["rationale"]
        else:
            withheld_info.append(new_item)

    logger.info(
        "Merged unpublished justification description data for BT-196(BT-5423)-LotsGroup",
    )
