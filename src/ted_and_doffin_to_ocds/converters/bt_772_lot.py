# converters/bt_772_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_late_tenderer_info_description(
    xml_content: str | bytes,
) -> dict[str, dict[str, list[dict[str, str]]]] | None:
    """Parse XML content to extract late tenderer information description (BT-772).

    This function extracts information about tenderer-related information that can be
    supplemented after the submission deadline from ProcurementProjectLot elements.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        A dictionary containing tender lots with submissionMethodDetails if found,
        otherwise None. Structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "submissionMethodDetails": str
                    }
                ]
            }
        }
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
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result: dict[str, dict] = {"tender": {"lots": []}}

    lots: list = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id: str = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description: list = lot.xpath(
            "cac:TenderingTerms/cac:TendererQualificationRequest"
            "[not(cbc:CompanyLegalFormCode)]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='reserved-procurement'])]"
            "[not(cac:SpecificTendererRequirement/cbc:TendererRequirementTypeCode[@listName='selection-criteria-source'])]"
            "/cac:SpecificTendererRequirement[cbc:TendererRequirementTypeCode/@listName='missing-info-submission']"
            "/cbc:Description/text()",
            namespaces=namespaces,
        )

        if description:
            result["tender"]["lots"].append(
                {"id": lot_id, "submissionMethodDetails": description[0]},
            )

    return result if result["tender"]["lots"] else None


def merge_late_tenderer_info_description(
    release_json: dict[str, dict],
    late_tenderer_info_description: dict[str, dict[str, list[dict[str, str]]]]
    | None = None,
) -> None:
    """Merge late tenderer information description into the release JSON.

    Appends or updates submissionMethodDetails in the tender lots with information
    about late tender submissions.

    Args:
        release_json: The target release JSON to update
        late_tenderer_info_description: Source data containing late tenderer information.
            If None, function returns without making changes.
    """
    if not late_tenderer_info_description:
        logger.warning("No late tenderer information description to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list = tender.setdefault("lots", [])

    for new_lot in late_tenderer_info_description["tender"]["lots"]:
        existing_lot: dict | None = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            if "submissionMethodDetails" in existing_lot:
                existing_lot["submissionMethodDetails"] += (
                    f" {new_lot['submissionMethodDetails']}"
                )
            else:
                existing_lot["submissionMethodDetails"] = new_lot[
                    "submissionMethodDetails"
                ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged late tenderer information description for %d lots",
        len(late_tenderer_info_description["tender"]["lots"]),
    )
