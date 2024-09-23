# converters/bt_772_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_late_tenderer_info_description(
    xml_content: str | bytes,
) -> dict | None:
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
            "cac:TenderingTerms/cac:TendererQualificationRequest[not(cbc:companyLegalFormCode)]"
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
    release_json: dict,
    late_tenderer_info_description: dict | None,
) -> None:
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
        f"Merged late tenderer information description for {len(late_tenderer_info_description['tender']['lots'])} lots",
    )
