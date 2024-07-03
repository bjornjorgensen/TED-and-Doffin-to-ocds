# converters/BT_759_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_received_submissions_count(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    }
    
    statistics_data = []
    
    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lot_id_elements = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        if lot_id_elements:
            lot_id = lot_id_elements[0]
        else:
            # If lot ID is not found, try to get it from LotResult ID
            lot_id_elements = lot_result.xpath("cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
            if lot_id_elements:
                lot_id = lot_id_elements[0]
            else:
                logger.warning(f"Lot ID not found for a LotResult")
                continue

        statistics = lot_result.xpath("efac:ReceivedSubmissionsStatistics/efbc:StatisticsNumeric/text()", namespaces=namespaces)
        
        if statistics:
            statistics_data.append({
                "relatedLot": lot_id,
                "value": int(statistics[0])
            })
    
    return statistics_data if statistics_data else None

def merge_received_submissions_count(release_json, statistics_data):
    if statistics_data:
        if "bids" not in release_json:
            release_json["bids"] = {}
        if "statistics" not in release_json["bids"]:
            release_json["bids"]["statistics"] = []
        
        for stat in statistics_data:
            existing_stat = next((s for s in release_json["bids"]["statistics"] if s["relatedLot"] == stat["relatedLot"]), None)
            if existing_stat:
                existing_stat["value"] = stat["value"]
            else:
                new_stat = {
                    "id": str(len(release_json["bids"]["statistics"]) + 1),
                    "value": stat["value"],
                    "relatedLot": stat["relatedLot"]
                }
                release_json["bids"]["statistics"].append(new_stat)