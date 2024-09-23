# converters/bt_115_GPA_Coverage.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_gpa_coverage(xml_content):
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

    result = {"tender": {"lots": [], "coveredBy": []}}

    # Process lots (BT-115-Lot)
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        gpa_coverage = lot.xpath(
            ".//cac:TenderingProcess/cbc:GovernmentAgreementConstraintIndicator/text()",
            namespaces=namespaces,
        )

        if gpa_coverage and gpa_coverage[0].lower() == "true":
            lot_data = {"id": lot_id, "coveredBy": ["GPA"]}
            result["tender"]["lots"].append(lot_data)

    # Process part (BT-115-part)
    part = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
        namespaces=namespaces,
    )
    if part:
        gpa_coverage = part[0].xpath(
            ".//cac:TenderingProcess/cbc:GovernmentAgreementConstraintIndicator/text()",
            namespaces=namespaces,
        )
        if gpa_coverage and gpa_coverage[0].lower() == "true":
            result["tender"]["coveredBy"].append("GPA")

    return result if result["tender"]["lots"] or result["tender"]["coveredBy"] else None


def merge_gpa_coverage(release_json, gpa_coverage_data):
    if not gpa_coverage_data:
        logger.warning("No GPA Coverage data to merge")
        return

    tender = release_json.setdefault("tender", {})

    # Merge lots
    if "lots" in gpa_coverage_data["tender"]:
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

    # Merge part
    if "coveredBy" in gpa_coverage_data["tender"]:
        tender.setdefault("coveredBy", []).extend(
            gpa_coverage_data["tender"]["coveredBy"],
        )

    logger.info(
        f"Merged GPA Coverage data for {len(gpa_coverage_data['tender']['lots'])} lots and part",
    )
