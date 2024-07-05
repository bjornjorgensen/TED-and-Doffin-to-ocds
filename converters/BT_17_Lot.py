# converters/BT_17_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_submission_electronic(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        submission_method_code = lot.xpath("cac:TenderingProcess/cbc:SubmissionMethodCode[@listName='esubmission']/text()", namespaces=namespaces)
        
        if submission_method_code:
            result["tender"]["lots"].append({
                "id": lot_id,
                "submissionTerms": {
                    "electronicSubmissionPolicy": submission_method_code[0]
                }
            })

    return result if result["tender"]["lots"] else None

def merge_submission_electronic(release_json, submission_electronic_data):
    if not submission_electronic_data:
        logger.warning("No Submission Electronic data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in submission_electronic_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {})["electronicSubmissionPolicy"] = new_lot["submissionTerms"]["electronicSubmissionPolicy"]
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Submission Electronic data for {len(submission_electronic_data['tender']['lots'])} lots")