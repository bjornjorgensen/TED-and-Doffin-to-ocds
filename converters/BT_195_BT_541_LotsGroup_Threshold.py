# converters/BT_195_BT_541_LotsGroup_Threshold.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_unpublished_award_criterion_number_threshold_lotsgroup(xml_content):
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

    xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-num']"
    
    for element in root.xpath(xpath, namespaces=namespaces):
        lots_group_id = element.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='LotsGroup']/text()", namespaces=namespaces)[0]
        
        withheld_item = {
            "id": f"awa-cri-num-threshold-{lots_group_id}",
            "field": "awa-cri-num",
            "name": "Award Criterion Number Threshold"
        }
        
        result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None

def merge_unpublished_award_criterion_number_threshold_lotsgroup(release_json, parsed_data):
    if not parsed_data:
        logger.info("No unpublished award criterion number threshold lotsgroup data to merge")
        return

    release_json.setdefault("withheldInformation", []).extend(parsed_data["withheldInformation"])
    logger.info(f"Merged {len(parsed_data['withheldInformation'])} unpublished award criterion number threshold lotsgroup items")