# converters/BT_805_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

# GPP criteria mapping table
GPP_CRITERIA_MAPPING = {
    "eu": "euGPPCriteria",
    "national": "nationalGPPCriteria",
    "other": "otherGPPCriteria"
}

def parse_green_procurement_criteria(xml_content):
    logger.info("Parsing BT-805-Lot: Green Procurement Criteria")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    logger.debug(f"Found {len(lot_elements)} lot elements")
    
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        gpp_criteria = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='gpp-criteria']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces
        )
        
        if gpp_criteria and gpp_criteria[0].lower() != "none":
            logger.debug(f"Lot {lot_id} has Green Procurement Criteria: {gpp_criteria}")
            lot_data = {
                "id": lot_id,
                "hasSustainability": True,
                "sustainability": []
            }
            
            for criterion in gpp_criteria:
                if criterion.lower() in GPP_CRITERIA_MAPPING:
                    lot_data["sustainability"].append({
                        "strategies": [GPP_CRITERIA_MAPPING[criterion.lower()]]
                    })
                else:
                    logger.warning(f"Unknown GPP criteria '{criterion}' for lot {lot_id}")
            
            if lot_data["sustainability"]:
                result["tender"]["lots"].append(lot_data)
        else:
            logger.debug(f"No valid Green Procurement Criteria found for lot {lot_id}")

    logger.info(f"Parsed Green Procurement Criteria for {len(result['tender']['lots'])} lots")
    return result

def merge_green_procurement_criteria(release_json, gpp_data):
    logger.info("Merging BT-805-Lot: Green Procurement Criteria")
    if not gpp_data["tender"]["lots"]:
        logger.warning("No Green Procurement Criteria data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for gpp_lot in gpp_data["tender"]["lots"]:
        lot_id = gpp_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)
        
        if existing_lot:
            existing_lot["hasSustainability"] = True
            existing_sustainability = existing_lot.setdefault("sustainability", [])
            for new_sustainability in gpp_lot["sustainability"]:
                if new_sustainability not in existing_sustainability:
                    existing_sustainability.append(new_sustainability)
            logger.debug(f"Updated Green Procurement Criteria for existing lot {lot_id}")
        else:
            lots.append(gpp_lot)
            logger.debug(f"Added new lot {lot_id} with Green Procurement Criteria")

    logger.info(f"Merged Green Procurement Criteria for {len(gpp_data['tender']['lots'])} lots")