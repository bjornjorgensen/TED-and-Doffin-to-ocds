# converters/OPP_032_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_revenues_allocation(xml_content):
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

    result = {"tender": {"lots": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        if tender_id:
            # Find the corresponding LotResult to get the lot_id
            lot_result = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:LotTender/cbc:ID[@schemeName='tender'] = '{tender_id[0]}']", namespaces=namespaces)
            if lot_result:
                lot_id = lot_result[0].xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
                if lot_id:
                    revenues_allocation = lot_tender.xpath("efac:RevenuesAllocation/efbc:RevenuesProcuringEntity/text()", namespaces=namespaces)
                    if revenues_allocation:
                        lot_data = {
                            "id": lot_id[0],
                            "revenuesAllocation": float(revenues_allocation[0])
                        }
                        result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_revenues_allocation(release_json, revenues_allocation_data):
    if not revenues_allocation_data:
        logger.warning("No revenues allocation data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in revenues_allocation_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot["revenuesAllocation"] = new_lot["revenuesAllocation"]
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged revenues allocation data for {len(revenues_allocation_data['tender']['lots'])} lots")