# converters/BT_195_BT_5421_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_unpublished_award_criterion_number_weight_lot(xml_content):
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

    xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-wei']"
    
    for element in root.xpath(xpath, namespaces=namespaces):
        lot_id = element.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        
        withheld_item = {
            "id": f"awa-cri-wei-{lot_id}",
            "field": "awa-cri-wei",
            "name": "Award Criterion Number Weight"
        }
        
        result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None

def merge_unpublished_award_criterion_number_weight_lot(release_json, parsed_data):
    if not parsed_data:
        logger.info("No unpublished award criterion number weight lot data to merge")
        return

    release_json.setdefault("withheldInformation", []).extend(parsed_data["withheldInformation"])
    logger.info(f"Merged {len(parsed_data['withheldInformation'])} unpublished award criterion number weight lot items")