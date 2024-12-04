# converters/bt_541_Lot_FixedNumber.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_fixed_number(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the award criterion fixed number (BT-541) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed award criterion fixed number data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        fixed_numbers = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efbc:ParameterNumeric/text()",
            namespaces=namespaces,
        )

        if fixed_numbers:
            lot_data = {
                "id": lot_id,
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
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criterion_fixed_number(
    release_json: dict[str, Any],
    award_criterion_fixed_number_data: dict[str, Any] | None,
) -> None:
    """Merge award criterion fixed number data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        award_criterion_fixed_number_data: The award criterion fixed number data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not award_criterion_fixed_number_data:
        logger.warning("No Award Criterion Fixed Number data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in award_criterion_fixed_number_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_criteria = existing_lot.setdefault("awardCriteria", {}).setdefault(
                "criteria",
                [],
            )
            if existing_criteria:
                existing_criterion = existing_criteria[0]
                existing_numbers = existing_criterion.setdefault("numbers", [])
                for new_number in new_lot["awardCriteria"]["criteria"][0]["numbers"]:
                    if new_number not in existing_numbers:
                        existing_numbers.append(new_number)
            else:
                existing_criteria.extend(new_lot["awardCriteria"]["criteria"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Award Criterion Fixed Number data for %d lots",
        len(award_criterion_fixed_number_data["tender"]["lots"]),
    )
