# converters/bt_5422_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_number_fixed_lotsgroup(xml_content):
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

        award_criteria = lot_group.xpath(
            ".//cac:AwardingCriterion/cac:SubordinateAwardingCriterion",
            namespaces=namespaces,
        )

        lot_group_data = {"id": lot_group_id, "awardCriteria": {"criteria": []}}

        for criterion in award_criteria:
            fixed_codes = criterion.xpath(
                ".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efbc:ParameterCode/text()",
                namespaces=namespaces,
            )

            if fixed_codes:
                criterion_data = {"numbers": [{"fixed": code} for code in fixed_codes]}
                lot_group_data["awardCriteria"]["criteria"].append(criterion_data)

        if lot_group_data["awardCriteria"]["criteria"]:
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_number_fixed_lotsgroup(
    release_json,
    award_criterion_number_fixed_lotsgroup_data,
):
    if not award_criterion_number_fixed_lotsgroup_data:
        logger.warning("No Award Criterion Number Fixed LotsGroup data to merge")
        return

    tender_lot_groups = release_json.setdefault("tender", {}).setdefault(
        "lotGroups",
        [],
    )

    for new_lot_group in award_criterion_number_fixed_lotsgroup_data["tender"][
        "lotGroups"
    ]:
        existing_lot_group = next(
            (lg for lg in tender_lot_groups if lg["id"] == new_lot_group["id"]),
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
                        crit
                        for crit in existing_criteria
                        if crit.get("numbers") == new_criterion["numbers"]
                    ),
                    None,
                )

                if existing_criterion:
                    existing_criterion["numbers"] = new_criterion["numbers"]
                else:
                    existing_criteria.append(new_criterion)
        else:
            tender_lot_groups.append(new_lot_group)

    logger.info(
        "Merged Award Criterion Number Fixed LotsGroup data for %d lot groups",
        len(award_criterion_number_fixed_lotsgroup_data["tender"]["lotGroups"]),
    )
