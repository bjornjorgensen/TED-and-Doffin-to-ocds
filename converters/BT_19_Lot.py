# converters/BT_19_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

NON_ELECTRONIC_SUBMISSION_CODES = {
    "ipr-iss": "Intellectual property right issues",
    "phy-mod": "Inclusion of a physical model",
    "sen-info": "Protection of particularly sensitive information",
    "sp-of-eq": "Buyer would need specialised office equipment",
    "tdf-non-av": "Tools, devices, or file formats not generally available"
}

def parse_nonelectronic_submission_justification(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        justification_code = lot.xpath(".//cac:TenderingProcess/cac:ProcessJustification/cbc:ProcessReasonCode[@listName='no-esubmission-justification']/text()", namespaces=namespaces)

        if justification_code:
            justification = NON_ELECTRONIC_SUBMISSION_CODES.get(justification_code[0], "Unknown justification")
            lot_data = {
                "id": lot_id,
                "submissionTerms": {
                    "nonElectronicSubmission": {
                        "rationale": justification
                    }
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_nonelectronic_submission_justification(release_json, justification_data):
    if not justification_data:
        logger.warning("No Nonelectronic Submission Justification data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "lots" not in release_json["tender"]:
        release_json["tender"]["lots"] = []

    for new_lot in justification_data["tender"]["lots"]:
        existing_lot = next((lot for lot in release_json["tender"]["lots"] if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            if "submissionTerms" not in existing_lot:
                existing_lot["submissionTerms"] = {}
            existing_lot["submissionTerms"]["nonElectronicSubmission"] = new_lot["submissionTerms"]["nonElectronicSubmission"]
        else:
            release_json["tender"]["lots"].append(new_lot)

    logger.info(f"Merged Nonelectronic Submission Justification data for {len(justification_data['tender']['lots'])} lots")