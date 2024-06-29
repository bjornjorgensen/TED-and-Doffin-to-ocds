# converters/OPP_032_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_revenues_allocation(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"tender": {"lots": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    for lot_tender in lot_tenders:
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
        
        revenue_allocation = lot_tender.xpath("efac:ContractTerm[efbc:TermCode/text()='all-rev-tic']/efbc:TermPercent/text()", namespaces=namespaces)
        
        if revenue_allocation:
            operator_revenue_share = float(revenue_allocation[0]) / 100
            result["tender"]["lots"].append({
                "id": lot_id,
                "contractTerms": {
                    "operatorRevenueShare": operator_revenue_share
                }
            })

    return result if result["tender"]["lots"] else None

def merge_revenues_allocation(release_json, revenues_allocation_data):
    if not revenues_allocation_data:
        logger.warning("No Revenues Allocation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in revenues_allocation_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(new_lot["contractTerms"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Revenues Allocation for {len(revenues_allocation_data['tender']['lots'])} lots")