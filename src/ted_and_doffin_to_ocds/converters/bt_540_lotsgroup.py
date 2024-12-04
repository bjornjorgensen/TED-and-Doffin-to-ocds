# converters/bt_540_LotsGroup.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_description_lots_group(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the award criterion description (BT-540) for procurement project lot groups from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed award criterion description data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lotGroups": [
                    {
                        "id": "GLO-0001",
                        "awardCriteria": {
                            "criteria": [
                                {
                                    "description": "Tenders with a quality score less than 65..."
                                }
                            ]
                        }
                    }
                ]
            }
        }
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

    result = {"tender": {"lotGroups": []}}

    lot_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lot_group in lot_groups:
        lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        criteria = lot_group.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/cbc:Description/text()",
            namespaces=namespaces,
        )

        if criteria:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {
                    "criteria": [{"description": criterion} for criterion in criteria],
                },
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_description_lots_group(
    release_json: dict[str, Any],
    award_criterion_description_data: dict[str, Any] | None,
) -> None:
    """Merge award criterion description data for lot groups into the main release JSON.

    Args:
        release_json: The main release JSON to merge data into
        award_criterion_description_data: The award criterion description data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not award_criterion_description_data:
        logger.warning("No Award Criterion Description data for lot groups to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_lot_group in award_criterion_description_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (lg for lg in existing_lot_groups if lg["id"] == new_lot_group["id"]),
            None,
        )
        if existing_lot_group:
            existing_criteria = existing_lot_group.setdefault(
                "awardCriteria",
                {},
            ).setdefault("criteria", [])
            for new_criterion in new_lot_group["awardCriteria"]["criteria"]:
                existing_criterion = next(
                    (
                        c
                        for c in existing_criteria
                        if c.get("description") == new_criterion["description"]
                    ),
                    None,
                )
                if existing_criterion:
                    existing_criterion.update(new_criterion)
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lot_groups.append(new_lot_group)

    logger.info(
        "Merged Award Criterion Description data for %d lot groups",
        len(award_criterion_description_data["tender"]["lotGroups"]),
    )
