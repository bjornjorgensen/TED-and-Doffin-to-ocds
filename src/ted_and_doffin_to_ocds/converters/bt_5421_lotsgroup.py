import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Mapping table for number weight codes
NUMBER_WEIGHT_MAPPING = {
    "dec-exa": "decimalExact",
    "dec-mid": "decimalRangeMiddle",
    "ord-imp": "order",
    "per-exa": "percentageExact",
    "per-mid": "percentageRangeMiddle",
    "poi-exa": "pointsExact",
    "poi-mid": "pointsRangeMiddle",
}


def parse_award_criterion_number_weight_lotsgroup(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criterion number weights from XML content for lot groups.

    Extracts weight codes associated with award criteria for each lot group from the XML.
    The codes are found under SubordinateAwardingCriterion elements with
    ParameterCode listName='number-weight' for LotsGroup.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lot groups with their award criteria
        number weights, or None if no relevant data found. Structure:
        {
            "tender": {
                "lotGroups": [
                    {
                        "id": str,
                        "awardCriteria": {
                            "criteria": [
                                {
                                    "numbers": [{"weight": str}]
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

        weight_codes = lot_group.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efbc:ParameterCode/text()",
            namespaces=namespaces,
        )

        criterion_data = [
            {"numbers": [{"weight": NUMBER_WEIGHT_MAPPING[code]}]}
            for code in weight_codes
            if code in NUMBER_WEIGHT_MAPPING
        ]

        if criterion_data:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {"criteria": criterion_data},
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_number_weight_lotsgroup(
    release_json: dict, award_criterion_number_weight_data: dict | None
) -> None:
    """Merge award criterion number weight data into the release JSON for lot groups.

    Takes the parsed weight codes and merges them into the appropriate lot groups
    in the release JSON. For each lot group, updates or adds award criteria numbers
    while avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        award_criterion_number_weight_data: The source data containing weight codes
            to merge, in the format returned by parse_award_criterion_number_weight_lotsgroup()

    Returns:
        None
    """
    if not award_criterion_number_weight_data:
        logger.warning("No Award Criterion Number Weight data to merge for lot groups")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_lot_group in award_criterion_number_weight_data["tender"]["lotGroups"]:
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
            existing_lot_groups.append(new_lot_group)

    logger.info(
        "Merged Award Criterion Number Weight data for %d lot groups",
        len(award_criterion_number_weight_data["tender"]["lotGroups"]),
    )
