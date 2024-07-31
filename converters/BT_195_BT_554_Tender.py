# converters/BT_195_BT_554_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_unpublished_subcontracting_description_tender(xml_content):
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

    xpath = "//efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-des']"
    
    elements = root.xpath(xpath, namespaces=namespaces)
    logger.info(f"Found {len(elements)} matching elements")

    for element in elements:
        field_identifier_code = element.xpath("efbc:FieldIdentifierCode/text()", namespaces=namespaces)[0]
        tender_id = element.xpath("ancestor::efac:LotTender/cbc:ID/text()", namespaces=namespaces)[0]
        
        withheld_item = {
            "id": f"{field_identifier_code}-{tender_id}",
            "field": "sub-des",
            "name": "Subcontracting Description"
        }
        
        result["withheldInformation"].append(withheld_item)
        logger.info(f"Added withheld item: {withheld_item}")

    return result if result["withheldInformation"] else None

def merge_unpublished_subcontracting_description_tender(release_json, parsed_data):
    if not parsed_data:
        logger.info("No unpublished subcontracting description tender data to merge")
        return

    release_json.setdefault("withheldInformation", []).extend(parsed_data["withheldInformation"])
    logger.info(f"Merged {len(parsed_data['withheldInformation'])} unpublished subcontracting description tender items")