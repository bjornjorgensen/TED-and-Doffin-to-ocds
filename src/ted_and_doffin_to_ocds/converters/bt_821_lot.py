import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_selection_criteria_source(xml_content):
    """
    Parse the XML content to extract the Selection Criteria Source for each lot.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        sources = lot.xpath(
            "cac:TenderingTerms/cac:TendererQualificationRequest"
            "[not(cbc:CompanyLegalFormCode)]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='missing-info-submission'])]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='reserved-procurement'])]"
            "/cac:SpecificTendererRequirement"
            "[cbc:TendererRequirementTypeCode/@listName='selection-criteria-source']"
            "/cbc:TendererRequirementTypeCode/text()",
            namespaces=namespaces,
        )

        if sources:
            lot_data = {"id": lot_id, "selectionCriteria": {"sources": sources}}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_selection_criteria_source(release_json, selection_criteria_data) -> None:
    """
    Merge the parsed Selection Criteria Source data into the main OCDS release JSON.
    """
    if not selection_criteria_data:
        logger.warning("No Selection Criteria Source data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in selection_criteria_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_criteria = existing_lot.setdefault("selectionCriteria", {})
            existing_sources = existing_criteria.setdefault("sources", [])
            existing_sources.extend(
                source
                for source in new_lot["selectionCriteria"]["sources"]
                if source not in existing_sources
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Selection Criteria Source data for %d lots",
        len(selection_criteria_data["tender"]["lots"]),
    )
