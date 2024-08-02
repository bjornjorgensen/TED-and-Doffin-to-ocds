# converters/BT_195_BT_541_Lot_Fixed.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_award_criterion_number_fixed(xml_content):
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

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-num']"
    
    for fields_privacy in root.xpath(xpath_query, namespaces=namespaces):
        lot_id = fields_privacy.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        field_identifier_code = fields_privacy.xpath("efbc:FieldIdentifierCode/text()", namespaces=namespaces)
        
        if lot_id and field_identifier_code:
            withheld_info = {
                "id": f"{field_identifier_code[0]}-fixed-{lot_id[0]}",
                "field": field_identifier_code[0],
                "name": "Award Criterion Number Fixed"
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def merge_unpublished_award_criterion_number_fixed(release_json, unpublished_award_criterion_number_fixed_data):
    if not unpublished_award_criterion_number_fixed_data:
        logger.warning("No Unpublished Award Criterion Number Fixed data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_withheld_info in unpublished_award_criterion_number_fixed_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_withheld_info["id"]), None)
        if existing_item:
            existing_item.update(new_withheld_info)
        else:
            existing_withheld_info.append(new_withheld_info)

    logger.info(f"Merged Unpublished Award Criterion Number Fixed data for {len(unpublished_award_criterion_number_fixed_data['withheldInformation'])} items")