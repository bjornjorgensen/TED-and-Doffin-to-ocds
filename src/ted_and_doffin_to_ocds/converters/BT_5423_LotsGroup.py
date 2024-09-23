# converters/BT_5423_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_number_threshold_lotsgroup(xml_content):
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

    lots_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lots_group in lots_groups:
        group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        award_criteria = lots_group.xpath(
            ".//cac:AwardingCriterion/cac:SubordinateAwardingCriterion",
            namespaces=namespaces,
        )

        group_data = {"id": group_id, "awardCriteria": {"criteria": []}}

        for criterion in award_criteria:
            threshold_codes = criterion.xpath(
                ".//efac:AwardCriterionParameter/efbc:ParameterCode[@listName='number-threshold']/text()",
                namespaces=namespaces,
            )

            criterion_data = {"numbers": []}

            for code in threshold_codes:
                threshold_value = (
                    "maximumBids"
                    if code == "max-pass"
                    else "minimumScore"
                    if code == "min-score"
                    else None
                )

                if threshold_value:
                    criterion_data["numbers"].append({"threshold": threshold_value})

            # Only add the criterion if it has valid threshold values
            if criterion_data["numbers"]:
                group_data["awardCriteria"]["criteria"].append(criterion_data)

        if group_data["awardCriteria"]["criteria"]:
            result["tender"]["lotGroups"].append(group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_number_threshold_lotsgroup(
    release_json,
    award_criterion_data,
):
    if not award_criterion_data:
        logger.warning("No Award Criterion Number Threshold LotsGroup data to merge")
        return

    tender_lot_groups = release_json.setdefault("tender", {}).setdefault(
        "lotGroups",
        [],
    )

    for new_group in award_criterion_data["tender"]["lotGroups"]:
        existing_group = next(
            (group for group in tender_lot_groups if group["id"] == new_group["id"]),
            None,
        )

        if existing_group:
            existing_criteria = existing_group.setdefault(
                "awardCriteria",
                {},
            ).setdefault("criteria", [])

            for new_criterion in new_group["awardCriteria"]["criteria"]:
                # Instead of creating a new criterion, merge the numbers into existing criteria
                if existing_criteria:
                    for existing_criterion in existing_criteria:
                        existing_numbers = existing_criterion.setdefault("numbers", [])
                        existing_numbers.extend(new_criterion["numbers"])
                else:
                    existing_criteria.append(new_criterion)
        else:
            tender_lot_groups.append(new_group)

    logger.info(
        f"Merged Award Criterion Number Threshold LotsGroup data for {len(award_criterion_data['tender']['lotGroups'])} lot groups",
    )
