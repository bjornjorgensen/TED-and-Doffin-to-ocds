# converters/BT_19_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

JUSTIFICATION_CODES = {
    "ipr-iss": "Intellectual property right issues",
    "phy-mod": "Inclusion of a physical model",
    "sen-info": "Protection of particularly sensitive information",
    "sp-of-eq": "Buyer would need specialised office equipment",
    "tdf-non-av": "Tools, devices, or file formats not generally available",
}


def parse_submission_nonelectronic_justification(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }
    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        justification_code = lot.xpath(
            "cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='no-esubmission-justification']/cbc:ProcessReasonCode/text()",
            namespaces=namespaces,
        )

        if justification_code:
            justification = JUSTIFICATION_CODES.get(justification_code[0])
            if justification:
                result["tender"]["lots"].append(
                    {
                        "id": lot_id,
                        "submissionTerms": {
                            "nonElectronicSubmission": {"rationale": justification},
                        },
                    },
                )

    return result if result["tender"]["lots"] else None


def merge_submission_nonelectronic_justification(release_json, justification_data):
    if not justification_data:
        logger.warning("No Submission Nonelectronic Justification data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in justification_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).setdefault(
                "nonElectronicSubmission", {},
            ).update(new_lot["submissionTerms"]["nonElectronicSubmission"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged Submission Nonelectronic Justification data for {len(justification_data['tender']['lots'])} lots",
    )
