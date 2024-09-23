# converters/BT_539_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_type_lots_group(xml_content):
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
            ".//cac:SubordinateAwardingCriterion/cbc:AwardingCriterionTypeCode[@listName='award-criterion-type']/text()",
            namespaces=namespaces,
        )

        if criteria:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {
                    "criteria": [{"type": criterion} for criterion in criteria],
                },
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_type_lots_group(release_json, award_criterion_type_data):
    if not award_criterion_type_data:
        logger.warning("No Award Criterion Type data for lot groups to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_lot_group in award_criterion_type_data["tender"]["lotGroups"]:
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
                        if c.get("type") == new_criterion["type"]
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
        f"Merged Award Criterion Type data for {len(award_criterion_type_data['tender']['lotGroups'])} lot groups",
    )
