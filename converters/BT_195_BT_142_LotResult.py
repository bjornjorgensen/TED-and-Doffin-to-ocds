# converters/BT_195_BT_142_LotResult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_winner_chosen(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"withheldInformation": []}

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        field_identifier_code = lot_result.xpath("efac:FieldsPrivacy/efbc:FieldIdentifierCode[text()='win-cho']/text()", namespaces=namespaces)
        lot_result_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        
        if field_identifier_code and lot_result_id:
            withheld_info = {
                "id": f"{field_identifier_code[0]}-{lot_result_id[0]}",
                "field": field_identifier_code[0],
                "name": "Winner Chosen"
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def merge_unpublished_winner_chosen(release_json, unpublished_winner_chosen_data):
    if not unpublished_winner_chosen_data:
        logger.warning("No Unpublished Winner Chosen data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_withheld_info in unpublished_winner_chosen_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_withheld_info["id"]), None)
        if existing_item:
            existing_item.update(new_withheld_info)
        else:
            existing_withheld_info.append(new_withheld_info)

    logger.info(f"Merged Unpublished Winner Chosen data for {len(unpublished_winner_chosen_data['withheldInformation'])} items")