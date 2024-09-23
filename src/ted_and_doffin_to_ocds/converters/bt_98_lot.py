# converters/bt_98_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_validity_deadline(xml_content):
    """
    Parse the XML content to extract the tender validity deadline for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed tender validity deadline data.
        None: If no relevant data is found.
    """
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
        duration_measure = lot.xpath(
            ".//cac:TenderingTerms/cac:TenderValidityPeriod/cbc:DurationMeasure",
            namespaces=namespaces,
        )

        if duration_measure:
            value = int(duration_measure[0].text)
            unit_code = duration_measure[0].get("unitCode")

            multiplier = {"DAY": 1, "WEEK": 7, "MONTH": 30, "YEAR": 365}.get(
                unit_code,
                1,
            )

            duration_in_days = value * multiplier

            lot_data = {
                "id": lot_id,
                "submissionTerms": {
                    "bidValidityPeriod": {"durationInDays": duration_in_days},
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_tender_validity_deadline(release_json, tender_validity_deadline_data):
    """
    Merge the parsed tender validity deadline data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        tender_validity_deadline_data (dict): The parsed tender validity deadline data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not tender_validity_deadline_data:
        logger.warning("No tender validity deadline data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in tender_validity_deadline_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).setdefault(
                "bidValidityPeriod",
                {},
            ).update(new_lot["submissionTerms"]["bidValidityPeriod"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged tender validity deadline data for {len(tender_validity_deadline_data['tender']['lots'])} lots",
    )
