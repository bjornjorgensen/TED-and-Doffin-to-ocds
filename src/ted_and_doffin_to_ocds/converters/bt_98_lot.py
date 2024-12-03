import logging

from lxml import etree

logger = logging.getLogger(__name__)

DURATION_MULTIPLIERS = {"DAY": 1, "WEEK": 7, "MONTH": 30, "YEAR": 365}


def parse_tender_validity_deadline(xml_content: str | bytes) -> dict | None:
    """Parse tender validity deadline information from XML for each lot.

    Extract information about the period for which tenders must remain valid
    as defined in BT-98.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "submissionTerms": {
                            "bidValidityPeriod": {
                                "durationInDays": int
                            }
                        }
                    }
                ]
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
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
            try:
                value = int(duration_measure[0].text)
                unit_code = duration_measure[0].get("unitCode")
                multiplier = DURATION_MULTIPLIERS.get(unit_code, 1)
                duration_in_days = value * multiplier

                lot_data = {
                    "id": lot_id,
                    "submissionTerms": {
                        "bidValidityPeriod": {"durationInDays": duration_in_days}
                    },
                }
                result["tender"]["lots"].append(lot_data)
            except (ValueError, TypeError):
                logger.warning("Invalid duration value for lot %s", lot_id)

    return result if result["tender"]["lots"] else None


def merge_tender_validity_deadline(
    release_json: dict, tender_validity_deadline_data: dict | None
) -> None:
    """Merge tender validity deadline data into the OCDS release.

    Updates the release JSON in-place by adding or updating submission terms
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        tender_validity_deadline_data: The parsed tender validity data
            in the same format as returned by parse_tender_validity_deadline().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not tender_validity_deadline_data:
        logger.info("No tender validity deadline data to merge")
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
        "Merged tender validity deadline data for %d lots",
        len(tender_validity_deadline_data["tender"]["lots"]),
    )
