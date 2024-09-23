# converters/BT_17_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_submission_electronic(xml_content):
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        submission_method = lot.xpath(
            "cac:TenderingProcess/cbc:SubmissionMethodCode[@listName='esubmission']/text()",
            namespaces=namespaces,
        )

        if lot_id and submission_method:
            lot_data = {
                "id": lot_id[0],
                "submissionTerms": {"electronicSubmissionPolicy": submission_method[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_submission_electronic(release_json, submission_electronic_data):
    if not submission_electronic_data:
        logger.warning("No Submission Electronic data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in submission_electronic_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(
                new_lot["submissionTerms"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged Submission Electronic data for {len(submission_electronic_data['tender']['lots'])} lots",
    )
