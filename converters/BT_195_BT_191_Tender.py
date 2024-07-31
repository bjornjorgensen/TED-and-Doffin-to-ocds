# converters/BT_195_BT_191_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_country_origin(xml_content):
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

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        field_identifier_code = lot_tender.xpath("efac:Origin/efac:FieldsPrivacy/efbc:FieldIdentifierCode[text()='cou-ori']/text()", namespaces=namespaces)
        
        if tender_id and field_identifier_code:
            withheld_info = {
                "id": f"{field_identifier_code[0]}-{tender_id[0]}",
                "field": field_identifier_code[0],
                "name": "Country Origin"
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def merge_unpublished_country_origin(release_json, unpublished_country_origin_data):
    if not unpublished_country_origin_data:
        logger.warning("No Unpublished Country Origin data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_withheld_info in unpublished_country_origin_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_withheld_info["id"]), None)
        if existing_item:
            existing_item.update(new_withheld_info)
        else:
            existing_withheld_info.append(new_withheld_info)

    logger.info(f"Merged Unpublished Country Origin data for {len(unpublished_country_origin_data['withheldInformation'])} items")