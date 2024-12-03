import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_gpa_coverage(xml_content: str | bytes) -> dict | None:
    """Parse GPA coverage information from XML for each lot.

    Extract information about whether the procurement is covered by the
    Government Procurement Agreement (GPA) as defined in BT-115.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "coveredBy": ["GPA"]  # Only present if GPA covered
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
        gpa_coverage = lot.xpath(
            "cac:TenderingProcess/cbc:GovernmentAgreementConstraintIndicator/text()",
            namespaces=namespaces,
        )

        if gpa_coverage and gpa_coverage[0].lower() == "true":
            lot_data = {"id": lot_id, "coveredBy": ["GPA"]}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_gpa_coverage(release_json: dict, gpa_coverage_data: dict | None) -> None:
    """Merge GPA coverage data into the OCDS release.

    Updates the release JSON in-place by adding or updating GPA coverage information
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        gpa_coverage_data: The parsed GPA coverage data
            in the same format as returned by parse_gpa_coverage().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not gpa_coverage_data:
        logger.info("No GPA coverage data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in gpa_coverage_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("coveredBy", []).extend(new_lot["coveredBy"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged GPA coverage data for %d lots", len(gpa_coverage_data["tender"]["lots"])
    )
