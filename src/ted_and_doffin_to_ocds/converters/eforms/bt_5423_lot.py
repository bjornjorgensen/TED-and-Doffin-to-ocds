# converters/bt_5423_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Mapping table for threshold codes
THRESHOLD_CODE_MAPPING = {"max-pass": "maximumBids", "min-score": "minimumScore"}


def parse_award_criterion_number_threshold_lot(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criterion number threshold codes from XML content.

    Extracts threshold codes associated with award criteria for each lot from the XML.
    The codes are found under SubordinateAwardingCriterion elements with
    ParameterCode listName='number-threshold'.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lots with their award criteria
        threshold codes, or None if no relevant data found. Structure:
        {
            "tender": {
                "lots": [
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        # Find all SubordinateAwardingCriterion elements in this lot
        subordinate_criteria = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion",
            namespaces=namespaces,
        )

        if subordinate_criteria:
            lot_data = {"id": lot_id, "awardCriteria": {"criteria": []}}

            # Process each SubordinateAwardingCriterion separately
            for criterion in subordinate_criteria:
                threshold_codes = criterion.xpath(
                    "./ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efbc:ParameterCode/text()",
                    namespaces=namespaces,
                )

                # Only add criteria that have valid threshold codes
                mapped_thresholds = [
                    {"threshold": THRESHOLD_CODE_MAPPING[code]}
                    for code in threshold_codes
                    if code in THRESHOLD_CODE_MAPPING
                ]

                if mapped_thresholds:
                    lot_data["awardCriteria"]["criteria"].append(
                        {"numbers": mapped_thresholds}
                    )

            # Only add the lot if it has criteria with numbers
            if lot_data["awardCriteria"]["criteria"]:
                result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criterion_number_threshold_lot(
    release_json: dict, award_criterion_number_threshold_data: dict | None
) -> None:
    """Merge award criterion number threshold codes into the release JSON.

    Takes the parsed threshold codes and merges them into the appropriate lots
    in the release JSON. For each lot, updates or adds award criteria numbers
    while avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        award_criterion_number_threshold_data: The source data containing threshold codes
            to merge, in the format returned by parse_award_criterion_number_threshold_lot()

    Returns:
        None

    """
    if not award_criterion_number_threshold_data:
        logger.warning("No Award Criterion Number Threshold data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in award_criterion_number_threshold_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )

        if existing_lot:
            existing_criteria = existing_lot.setdefault("awardCriteria", {}).setdefault(
                "criteria",
                [],
            )

            # Handle merging based on the existing criteria
            if (
                len(existing_criteria) == 1
                and "id" in existing_criteria[0]
                and not existing_criteria[0].get("numbers")
            ):
                # Special case: If there's exactly one existing criterion with an ID and no numbers,
                # merge the first new criterion into it
                for i, new_criterion in enumerate(new_lot["awardCriteria"]["criteria"]):
                    if i == 0:
                        # Merge the first new criterion into the existing one
                        existing_criteria[0].setdefault("numbers", []).extend(
                            new_criterion["numbers"]
                        )
                    else:
                        # Add any additional criteria separately
                        existing_criteria.append(new_criterion)
            else:
                # Default case: Preserve each new criterion separately
                for new_criterion in new_lot["awardCriteria"]["criteria"]:
                    existing_criteria.append(new_criterion)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Award Criterion Number Threshold data for %d lots",
        len(award_criterion_number_threshold_data["tender"]["lots"]),
    )
