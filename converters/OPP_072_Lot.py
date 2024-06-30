# converters/OPP_072_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_quality_target_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        customer_services = lot.xpath("cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='customer-service']", namespaces=namespaces)
        
        if customer_services:
            lot_data = {
                "id": lot_id,
                "contractTerms": {
                    "customerServices": []
                }
            }
            
            for service in customer_services:
                service_type = service.xpath("cbc:ExecutionRequirementCode/text()", namespaces=namespaces)
                description = service.xpath("cbc:Description/text()", namespaces=namespaces)
                
                service_data = {}
                if service_type:
                    service_data["type"] = service_type[0]
                if description:
                    service_data["description"] = description[0]
                
                if service_data:
                    lot_data["contractTerms"]["customerServices"].append(service_data)
            
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_quality_target_description(release_json, quality_target_description_data):
    if not quality_target_description_data:
        logger.warning("No Quality Target Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in quality_target_description_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_contract_terms = existing_lot.setdefault("contractTerms", {})
            existing_customer_services = existing_contract_terms.setdefault("customerServices", [])
            
            for new_service in new_lot["contractTerms"]["customerServices"]:
                existing_service = next((service for service in existing_customer_services if service.get("type") == new_service.get("type")), None)
                if existing_service:
                    existing_service.update(new_service)
                else:
                    existing_customer_services.append(new_service)
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Quality Target Description for {len(quality_target_description_data['tender']['lots'])} lots")