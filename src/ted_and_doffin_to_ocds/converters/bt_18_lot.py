# converters/bt_18_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_submission_url(xml_content):
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
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        submission_url = lot.xpath(
            "cac:TenderingTerms/cac:TenderRecipientparty/cbc:EndpointID/text()",
            namespaces=namespaces,
        )

        lot_data = {"id": lot_id}

        if submission_url:
            lot_data["submissionMethodDetails"] = submission_url[0]

        result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_submission_url(release_json, submission_url_data):
    if not submission_url_data:
        logger.warning("No Submission URL data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in submission_url_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot.get("id") == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.update(new_lot)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Submission URL data for %d lots",
        len(submission_url_data["tender"]["lots"]),
    )
