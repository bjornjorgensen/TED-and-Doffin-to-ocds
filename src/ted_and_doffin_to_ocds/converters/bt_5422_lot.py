# converters/bt_5422_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_number_fixed(xml_content):
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        award_criteria = lot.xpath(
            ".//cac:AwardingCriterion/cac:SubordinateAwardingCriterion",
            namespaces=namespaces,
        )

        lot_data = {"id": lot_id, "awardCriteria": {"criteria": []}}

        for criterion in award_criteria:
            fixed_codes = criterion.xpath(
                ".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efbc:ParameterCode/text()",
                namespaces=namespaces,
            )

            if fixed_codes:
                criterion_data = {"numbers": [{"fixed": code} for code in fixed_codes]}
                lot_data["awardCriteria"]["criteria"].append(criterion_data)

        if lot_data["awardCriteria"]["criteria"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criterion_number_fixed(release_json, award_criterion_number_fixed_data):
    if not award_criterion_number_fixed_data:
        logger.warning("No Award Criterion Number Fixed data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in award_criterion_number_fixed_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]),
            None,
        )

        if existing_lot:
            existing_criteria = existing_lot.setdefault("awardCriteria", {}).setdefault(
                "criteria",
                [],
            )

            for new_criterion in new_lot["awardCriteria"]["criteria"]:
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
            tender_lots.append(new_lot)

    logger.info(
        f"Merged Award Criterion Number Fixed data for {len(award_criterion_number_fixed_data['tender']['lots'])} lots",
    )
