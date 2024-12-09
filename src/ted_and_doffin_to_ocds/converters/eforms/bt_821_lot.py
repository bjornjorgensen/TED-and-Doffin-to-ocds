import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_selection_criteria_source(xml_content: str | bytes) -> dict | None:
    """Parse BT-821: Selection criteria source locations for lots.

    Extracts information about where selection criteria are defined (e.g. procurement
    documents or ESPD).

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "selectionCriteria": {
                                "sources": [str]
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            sources = lot.xpath(
                "cac:TenderingTerms/cac:TendererQualificationRequest"
                "[not(cbc:CompanyLegalFormCode)]"
                "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='missing-info-submission'])]"
                "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='reserved-procurement'])]"
                "/cac:SpecificTendererRequirement"
                "[cbc:TendererRequirementTypeCode/@listName='selection-criteria-source']"
                "/cbc:TendererRequirementTypeCode/text()",
                namespaces=NAMESPACES,
            )

            if sources:
                logger.info(
                    "Found selection criteria sources for lot %s: %s", lot_id, sources
                )
                result["tender"]["lots"].append(
                    {"id": lot_id, "selectionCriteria": {"sources": sources}}
                )

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing selection criteria sources")
        return None


def merge_selection_criteria_source(
    release_json: dict, source_data: dict | None
) -> None:
    """Merge selection criteria source data into the release JSON.

    Updates or adds selection criteria sources to lots.

    Args:
        release_json: Main OCDS release JSON to update
        source_data: Selection criteria source data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Handles duplicate sources

    """
    if not source_data:
        logger.warning("No Selection Criteria Source data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in source_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            criteria = existing_lot.setdefault("selectionCriteria", {})
            sources = criteria.setdefault("sources", [])
            # Add new sources avoiding duplicates
            sources.extend(
                source
                for source in new_lot["selectionCriteria"]["sources"]
                if source not in sources
            )
        else:
            lots.append(new_lot)

    logger.info(
        "Merged Selection Criteria Source data for %d lots",
        len(source_data["tender"]["lots"]),
    )
