# converters/BT_195_BT_543_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_unpublished_award_criteria_complicated_lot(xml_content):
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

    xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-com']"
    
    elements = root.xpath(xpath, namespaces=namespaces)
    logger.info(f"Found {len(elements)} matching elements")

    for element in elements:
        field_identifier_code = element.xpath("efbc:FieldIdentifierCode/text()", namespaces=namespaces)[0]
        lot_id = element.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        
        withheld_item = {
            "id": f"{field_identifier_code}-{lot_id}",
            "field": "awa-cri-com",
            "name": "Award Criteria Complicated"
        }
        
        result["withheldInformation"].append(withheld_item)
        logger.info(f"Added withheld item: {withheld_item}")

    return result if result["withheldInformation"] else None

def merge_unpublished_award_criteria_complicated_lot(release_json, parsed_data):
    if not parsed_data:
        logger.info("No unpublished award criteria complicated lot data to merge")
        return

    release_json.setdefault("withheldInformation", []).extend(parsed_data["withheldInformation"])
    logger.info(f"Merged {len(parsed_data['withheldInformation'])} unpublished award criteria complicated lot items")