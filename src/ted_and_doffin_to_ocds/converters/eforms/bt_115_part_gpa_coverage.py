import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_gpa_coverage_part(xml_content: str | bytes) -> dict | None:
    """Parse GPA coverage information from XML for the part.

    Extract information about whether the procurement is covered by the
    Government Procurement Agreement (GPA) as defined in BT-115.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "coveredBy": ["GPA"]  # Only present if GPA covered
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

    part = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
        namespaces=namespaces,
    )
    if not part:
        return None

    gpa_coverage = part[0].xpath(
        "cac:TenderingProcess/cbc:GovernmentAgreementConstraintIndicator/text()",
        namespaces=namespaces,
    )

    if gpa_coverage and gpa_coverage[0].lower() == "true":
        return {"tender": {"coveredBy": ["GPA"]}}

    return None


def merge_gpa_coverage_part(
    release_json: dict, gpa_coverage_part_data: dict | None
) -> None:
    """Merge GPA coverage part data into the OCDS release.

    Updates the release JSON in-place by adding GPA coverage information
    to the tender.

    Args:
        release_json: The main OCDS release JSON to be updated.
        gpa_coverage_part_data: The parsed GPA coverage data
            in the same format as returned by parse_gpa_coverage_part().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not gpa_coverage_part_data:
        logger.info("No GPA coverage part data to merge")
        return

    tender = release_json.setdefault("tender", {})

    if "coveredBy" in gpa_coverage_part_data["tender"]:
        tender.setdefault("coveredBy", []).extend(
            gpa_coverage_part_data["tender"]["coveredBy"]
        )
        logger.info("Merged GPA coverage part data")
