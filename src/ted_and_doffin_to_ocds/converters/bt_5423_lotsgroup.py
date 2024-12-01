# converters/bt_5423_LotsGroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Mapping table for threshold codes
THRESHOLD_CODE_MAPPING = {"max-pass": "maximumBids", "min-score": "minimumScore"}


def parse_award_criterion_number_threshold_lotsgroup(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criterion number threshold codes from XML content for lot groups.

    Extracts threshold codes associated with award criteria for each lot group from the XML.
    The codes are found under SubordinateAwardingCriterion elements with
    ParameterCode listName='number-threshold' for LotsGroup.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lot groups with their award criteria
        threshold codes, or None if no relevant data found. Structure:
        {
            "tender": {
                "lotGroups": [
                    {
                        "id": str,
                        "awardCriteria": {
                            "criteria": [
                                {
                                    "numbers": [{"threshold": str}]
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

        threshold_codes = lot_group.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efbc:ParameterCode/text()",
            namespaces=namespaces,
        )

        if threshold_codes:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {
                    "criteria": [
                        {
                            "numbers": [
                                {"threshold": THRESHOLD_CODE_MAPPING[code]}
                                for code in threshold_codes
                                if code in THRESHOLD_CODE_MAPPING
                            ]
                        }
                    ]
                },
            }
            if lot_group_data["awardCriteria"]["criteria"][0]["numbers"]:
                result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_number_threshold_lotsgroup(
    release_json: dict, award_criterion_number_threshold_data: dict | None
) -> None:
    """Merge award criterion number threshold codes into the release JSON for lot groups.

    Takes the parsed threshold codes and merges them into the appropriate lot groups
    in the release JSON. For each lot group, updates or adds award criteria numbers
    while avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        award_criterion_number_threshold_data: The source data containing threshold codes
            to merge, in the format returned by parse_award_criterion_number_threshold_lotsgroup()

    Returns:
        None
    """
    if not award_criterion_number_threshold_data:
        logger.warning(
            "No Award Criterion Number Threshold data to merge for lot groups"
        )
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_group in award_criterion_number_threshold_data["tender"]["lotGroups"]:
        existing_group = next(
            (group for group in existing_lot_groups if group["id"] == new_group["id"]),
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
            existing_lot_groups.append(new_group)

    logger.info(
        "Merged Award Criterion Number Threshold data for %d lot groups",
        len(award_criterion_number_threshold_data["tender"]["lotGroups"]),
    )
