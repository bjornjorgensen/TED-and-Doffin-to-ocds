# converters/BT_195_BT_5422_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def BT_195_parse_unpublished_award_criterion_number_fixed_lot_bt5422(xml_content):
    """
    Parse the XML content to extract the unpublished award criterion number fixed for lots (BT-195, BT-5422).

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished award criterion number fixed data.
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

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-fix']"
    fields_privacy = root.xpath(xpath_query, namespaces=namespaces)

    for field_privacy in fields_privacy:
        lot_id = field_privacy.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        if lot_id:
            withheld_info = {
                "id": f"awa-cri-fix-{lot_id[0]}",
                "field": "awa-cri-fix",
                "name": "Award Criterion Number Fixed"
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def BT_195_merge_unpublished_award_criterion_number_fixed_lot_bt5422(release_json, unpublished_award_criterion_number_fixed_data):
    """
    Merge the parsed unpublished award criterion number fixed data (BT-195, BT-5422) into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_award_criterion_number_fixed_data (dict): The parsed unpublished award criterion number fixed data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_award_criterion_number_fixed_data:
        logger.warning("No unpublished award criterion number fixed data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_info in unpublished_award_criterion_number_fixed_data["withheldInformation"]:
        existing_info = next((info for info in existing_withheld_info if info["id"] == new_info["id"]), None)
        if existing_info:
            existing_info.update(new_info)
        else:
            existing_withheld_info.append(new_info)

    logger.info(f"Merged unpublished award criterion number fixed data for {len(unpublished_award_criterion_number_fixed_data['withheldInformation'])} items")