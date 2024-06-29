# converters/BT_98_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_validity_deadline(xml_content):
    logger.info("Parsing BT-98-Lot: Tender Validity Deadline")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        validity_period = lot.xpath("cac:TenderingTerms/cac:TenderValidityPeriod/cbc:DurationMeasure", namespaces=namespaces)
        
        if validity_period:
            duration = int(validity_period[0].text)
            unit_code = validity_period[0].get('unitCode')
            
            multiplier = {
                'DAY': 1,
                'WEEK': 7,
                'MONTH': 30,
                'YEAR': 365
            }.get(unit_code, 1)
            
            duration_in_days = duration * multiplier
            
            result["tender"]["lots"].append({
                "id": lot_id,
                "submissionTerms": {
                    "bidValidityPeriod": {
                        "durationInDays": duration_in_days
                    }
                }
            })
            logger.debug(f"Parsed Tender Validity Deadline for lot {lot_id}: {duration_in_days} days")
        else:
            logger.debug(f"No Tender Validity Deadline found for lot {lot_id}")

    return result

def merge_tender_validity_deadline(release_json, validity_deadline_data):
    logger.info("Merging BT-98-Lot: Tender Validity Deadline")
    if not validity_deadline_data["tender"]["lots"]:
        logger.warning("No Tender Validity Deadline data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in validity_deadline_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {})["bidValidityPeriod"] = new_lot["submissionTerms"]["bidValidityPeriod"]
            logger.debug(f"Updated Tender Validity Deadline for existing lot {new_lot['id']}")
        else:
            lots.append(new_lot)
            logger.debug(f"Added new lot {new_lot['id']} with Tender Validity Deadline")

    logger.info(f"Merged Tender Validity Deadline for {len(validity_deadline_data['tender']['lots'])} lots")