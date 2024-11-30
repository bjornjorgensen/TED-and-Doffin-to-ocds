# converters/bt_5421_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_number_weight_lot(xml_content):
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

    number_weight_mapping = {
        "dec-exa": "decimalExact",
        "dec-mid": "decimalRangeMiddle",
        "ord-imp": "order",
        "per-exa": "percentageExact",
        "per-mid": "percentageRangeMiddle",
        "poi-exa": "pointsExact",
        "poi-mid": "pointsRangeMiddle",
    }

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        award_criteria = lot.xpath(
            ".//cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion",
            namespaces=namespaces,
        )

        lot_data = {"id": lot_id, "awardCriteria": {"criteria": []}}

        for criterion in award_criteria:
            criterion_data = {"numbers": []}

            number_weights = criterion.xpath(
                ".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efbc:ParameterCode/text()",
                namespaces=namespaces,
            )

            for weight in number_weights:
                if weight in number_weight_mapping:
                    criterion_data["numbers"].append(
                        {"weight": number_weight_mapping[weight]},
                    )

            if criterion_data["numbers"]:
                lot_data["awardCriteria"]["criteria"].append(criterion_data)

        if lot_data["awardCriteria"]["criteria"]:
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criterion_number_weight_lot(
    release_json,
    lot_award_criterion_number_weight_data,
) -> None:
    if not lot_award_criterion_number_weight_data:
        logger.warning("No Lot Award Criterion Number Weight data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_award_criterion_number_weight_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
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
                        c
                        for c in existing_criteria
                        if c.get("id") == new_criterion.get("id")
                    ),
                    None,
                )

                if existing_criterion:
                    existing_numbers = existing_criterion.setdefault("numbers", [])
                    for new_number in new_criterion["numbers"]:
                        existing_number = next(
                            (
                                n
                                for n in existing_numbers
                                if n.get("id") == new_number.get("id")
                            ),
                            None,
                        )
                        if existing_number:
                            existing_number.update(new_number)
                        else:
                            existing_numbers.append(new_number)
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Lot Award Criterion Number Weight data for %d lots",
        len(lot_award_criterion_number_weight_data["tender"]["lots"]),
    )
