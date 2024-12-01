# converters/bt_5422_LotsGroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_number_fixed_lotsgroup(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criterion number fixed codes from XML content for lot groups.

    Extracts fixed codes associated with award criteria for each lot group from the XML.
    The codes are found under SubordinateAwardingCriterion elements with
    ParameterCode listName='number-fixed' for LotsGroup.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lot groups with their award criteria
        fixed codes, or None if no relevant data found. Structure:
        {
            "tender": {
                "lotGroups": [
                    {
                        "id": str,
                        "awardCriteria": {
                            "criteria": [
                                {
                                    "numbers": [{"fixed": str}]
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

        fixed_codes = lot_group.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efbc:ParameterCode/text()",
            namespaces=namespaces,
        )

        if fixed_codes:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {
                    "criteria": [{"numbers": [{"fixed": code} for code in fixed_codes]}]
                },
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_number_fixed_lotsgroup(
    release_json: dict, award_criterion_number_fixed_data: dict | None
) -> None:
    """Merge award criterion number fixed codes into the release JSON for lot groups.

    Takes the parsed fixed codes and merges them into the appropriate lot groups
    in the release JSON. For each lot group, updates or adds award criteria numbers
    while avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        award_criterion_number_fixed_data: The source data containing fixed codes
            to merge, in the format returned by parse_award_criterion_number_fixed_lotsgroup()

    Returns:
        None
    """
    if not award_criterion_number_fixed_data:
        logger.warning("No Award Criterion Number Fixed data to merge for lot groups")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_lot_group in award_criterion_number_fixed_data["tender"]["lotGroups"]:
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
            existing_lot_groups.append(new_lot_group)

    logger.info(
        "Merged Award Criterion Number Fixed data for %d lot groups",
        len(award_criterion_number_fixed_data["tender"]["lotGroups"]),
    )
