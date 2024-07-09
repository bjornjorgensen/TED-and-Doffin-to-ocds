# converters/BT_195_BT_160_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_unpublished_concession_revenue_buyer(xml_content):
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

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        field_identifier_code = lot_tender.xpath("efac:ConcessionRevenue/efac:FieldsPrivacy/efbc:FieldIdentifierCode[text()='con-rev-buy']/text()", namespaces=namespaces)
        lot_tender_id = lot_tender.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        
        if field_identifier_code and lot_tender_id:
            withheld_info = {
                "id": f"{field_identifier_code[0]}-{lot_tender_id[0]}",
                "field": field_identifier_code[0],
                "name": "Concession Revenue Buyer"
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def merge_unpublished_concession_revenue_buyer(release_json, unpublished_concession_revenue_buyer_data):
    if not unpublished_concession_revenue_buyer_data:
        logger.warning("No Unpublished Concession Revenue Buyer data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_withheld_info in unpublished_concession_revenue_buyer_data["withheldInformation"]:
        existing_item = next((item for item in existing_withheld_info if item["id"] == new_withheld_info["id"]), None)
        if existing_item:
            existing_item.update(new_withheld_info)
        else:
            existing_withheld_info.append(new_withheld_info)

    logger.info(f"Merged Unpublished Concession Revenue Buyer data for {len(unpublished_concession_revenue_buyer_data['withheldInformation'])} items")