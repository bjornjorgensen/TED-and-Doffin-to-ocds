import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_fixed_number_lotsgroup(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the award criterion fixed number (BT-541) for procurement project lot groups from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed award criterion fixed number data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lotGroups": [
                    {
                        "id": "GLO-0001",
                        "awardCriteria": {
                            "criteria": [
                                {
                                    "numbers": [
                                        {
                                            "number": 50
                                        }
                                    ]
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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"tender": {"lotGroups": []}}

    lot_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lot_group in lot_groups:
        lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        fixed_numbers = lot_group.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efbc:ParameterNumeric/text()",
            namespaces=namespaces,
        )

        if fixed_numbers:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {
                    "criteria": [
                        {
                            "numbers": [
                                {"number": float(number)} for number in fixed_numbers
                            ],
                        },
                    ],
                },
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_fixed_number_lotsgroup(
    release_json: dict[str, Any],
    award_criterion_fixed_number_data: dict[str, Any] | None,
) -> None:
    """Merge award criterion fixed number data into the release JSON for lot groups.

    Args:
        release_json: The main release JSON to merge data into
        award_criterion_fixed_number_data: The award criterion fixed number data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not award_criterion_fixed_number_data:
        logger.warning("No Award Criterion Fixed Number data to merge for lot groups")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_lot_group in award_criterion_fixed_number_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (
                group
                for group in existing_lot_groups
                if group["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            existing_criteria = existing_lot_group.setdefault(
                "awardCriteria", {}
            ).setdefault(
                "criteria",
                [],
            )
            if existing_criteria:
                existing_criterion = existing_criteria[0]
                existing_numbers = existing_criterion.setdefault("numbers", [])
                for new_number in new_lot_group["awardCriteria"]["criteria"][0][
                    "numbers"
                ]:
                    if new_number not in existing_numbers:
                        existing_numbers.append(new_number)
            else:
                existing_criteria.extend(new_lot_group["awardCriteria"]["criteria"])
        else:
            existing_lot_groups.append(new_lot_group)

    logger.info(
        "Merged Award Criterion Fixed Number data for %d lot groups",
        len(award_criterion_fixed_number_data["tender"]["lotGroups"]),
    )
