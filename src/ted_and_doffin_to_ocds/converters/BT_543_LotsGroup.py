# converters/BT_543_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criteria_complicated_lotsgroup(xml_content):
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
        calculation_expression = lot_group.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cbc:CalculationExpression/text()",
            namespaces=namespaces,
        )

        if calculation_expression:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {"weightingDescription": calculation_expression[0]},
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criteria_complicated_lotsgroup(release_json, award_criteria_data):
    if not award_criteria_data:
        logger.warning("No award criteria complicated data for lot groups to merge")
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault(
        "lotGroups",
        [],
    )

    for new_lot_group in award_criteria_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (
                group
                for group in existing_lot_groups
                if group["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            existing_lot_group.setdefault("awardCriteria", {}).update(
                new_lot_group["awardCriteria"],
            )
        else:
            existing_lot_groups.append(new_lot_group)

    logger.info(
        f"Merged award criteria complicated data for {len(award_criteria_data['tender']['lotGroups'])} lot groups",
    )
