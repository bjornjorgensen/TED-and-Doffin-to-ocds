import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Map selection criterion codes to their types
SELECTION_CRITERION_TYPE_MAP = {
    "slc-abil": "technical",
    "slc-abil-facil-res": "technical",
    "slc-abil-facil-tools": "technical",
    "slc-abil-mgmt-env": "technical",
    "slc-abil-mgmt-qual": "technical",
    "slc-abil-mgmt-supply": "technical",
    "slc-abil-qual-inst": "technical",
    "slc-abil-qual-smp-w-autent": "technical",
    "slc-abil-qual-smp-wo-autent": "technical",
    "slc-abil-ref-services": "technical",
    "slc-abil-ref-work": "technical",
    "slc-abil-staff-qual": "technical",
    "slc-abil-staff-tech-ctrl": "technical",
    "slc-abil-staff-tech-work": "technical",
    "slc-abil-staff-yrly-avg-mp": "technical",
    "slc-abil-staff-yrly-no-mgmt": "technical",
    "slc-abil-subc": "technical",
    "slc-sche": "other",
    "slc-sche-env-cert-indep": "other",
    "slc-sche-qu-cert-indep": "other",
    "slc-sec": "other",
    "slc-sec-inf": "other",
    "slc-sec-proc": "other",
    "slc-sec-supply": "other",
    "slc-stand": "economic",
    "slc-stand-ins": "economic",
    "slc-stand-other": "economic",
    "slc-stand-ration": "economic",
    "slc-stand-to-avg": "economic",
    "slc-stand-to-gen": "economic",
    "slc-stand-to-spec": "economic",
    "slc-stand-to-spec-avg": "economic",
    "slc-suit": "suitability",
    "slc-suit-auth-mbrshp": "suitability",
    "slc-suit-ref-prof": "suitability",
    "slc-suit-reg-trade": "suitability",
    "slc-suit-reg-prof": "suitability",
}


def parse_selection_criteria_809(
    xml_content: str | bytes,
) -> dict[str, dict[str, list[dict[str, str]]]] | None:
    """Parse XML content to extract selection criteria (BT-809).

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        A dictionary containing tender lots with selection criteria if found,
        otherwise None.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root: etree._Element = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria_codes = lot.xpath(
            "cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
            "/efext:EformsExtension/efac:SelectionCriteria/cbc:TendererRequirementTypeCode"
            "[@listName='selection-criterion']/text()",
            namespaces=namespaces,
        )

        if criteria_codes:
            criteria = []
            for code in criteria_codes:
                criterion_type = SELECTION_CRITERION_TYPE_MAP.get(code)
                if criterion_type:
                    criteria.append({"type": criterion_type, "subType": code})

            result["tender"]["lots"].append(
                {"id": lot_id, "selectionCriteria": {"criteria": criteria}}
            )

    return result if result["tender"]["lots"] else None


def merge_selection_criteria_809(
    release_json: dict, selection_criteria: dict | None = None
) -> None:
    """Merge selection criteria into the release JSON.

    Args:
        release_json: The target release JSON to update
        selection_criteria: Source data containing selection criteria.
            If None, function returns without making changes.

    """
    if not selection_criteria:
        logger.warning("No selection criteria to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in selection_criteria["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            if "selectionCriteria" not in existing_lot:
                existing_lot["selectionCriteria"] = {"criteria": []}
            existing_lot["selectionCriteria"]["criteria"].extend(
                new_lot["selectionCriteria"]["criteria"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged selection criteria for %d lots",
        len(selection_criteria["tender"]["lots"]),
    )
