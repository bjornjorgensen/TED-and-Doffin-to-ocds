# converters/BT_195_BT_5421_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def BT_195_parse_unpublished_award_criterion_number_weight_lotsgroup_bt5421(xml_content):
    """
    Parse the XML content to extract the unpublished award criterion number weight for lots groups (BT-195, BT-5421).

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished award criterion number weight data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"withheldInformation": []}

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-wei']"
    fields_privacy = root.xpath(xpath_query, namespaces=namespaces)

    for field_privacy in fields_privacy:
        lots_group_id = field_privacy.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='LotsGroup']/text()", namespaces=namespaces)
        if lots_group_id:
            withheld_info = {
                "id": f"awa-cri-wei-{lots_group_id[0]}",
                "field": "awa-cri-wei",
                "name": "Award Criterion Number Weight"
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def BT_195_merge_unpublished_award_criterion_number_weight_lotsgroup_bt5421(release_json, unpublished_award_criterion_number_weight_data):
    """
    Merge the parsed unpublished award criterion number weight data (BT-195, BT-5421) into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_award_criterion_number_weight_data (dict): The parsed unpublished award criterion number weight data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_award_criterion_number_weight_data:
        logger.warning("No unpublished award criterion number weight data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_info in unpublished_award_criterion_number_weight_data["withheldInformation"]:
        existing_info = next((info for info in existing_withheld_info if info["id"] == new_info["id"]), None)
        if existing_info:
            existing_info.update(new_info)
        else:
            existing_withheld_info.append(new_info)

    logger.info(f"Merged unpublished award criterion number weight data for {len(unpublished_award_criterion_number_weight_data['withheldInformation'])} items")