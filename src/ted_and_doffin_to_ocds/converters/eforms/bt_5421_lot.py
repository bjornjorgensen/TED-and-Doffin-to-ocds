# converters/bt_5421_Lot.py

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


def parse_award_criterion_number_weight_lot(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criterion number weights from XML content.

    Extracts weight codes associated with award criteria for each lot from the XML.
    The codes are found under SubordinateAwardingCriterion elements with
    ParameterCode listName='number-weight'.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lots with their award criteria
        number weights, or None if no relevant data found. Structure:
        {
            "tender": {
                "lots": [
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

        weight_codes = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efbc:ParameterCode/text()",
            namespaces=namespaces,
        )

        criterion_data = [
            {"numbers": [{"weight": NUMBER_WEIGHT_MAPPING[code]}]}
            for code in weight_codes
            if code in NUMBER_WEIGHT_MAPPING
        ]

        if criterion_data:
            lot_data = {"id": lot_id, "awardCriteria": {"criteria": criterion_data}}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criterion_number_weight_lot(
    release_json: dict, award_criterion_number_weight_data: dict | None
) -> None:
    """Merge award criterion number weight data into the release JSON.

    Takes the parsed weight codes and merges them into the appropriate lots
    in the release JSON. For each lot, updates or adds award criteria numbers
    while avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        award_criterion_number_weight_data: The source data containing weight codes
            to merge, in the format returned by parse_award_criterion_number_weight_lot()

    Returns:
        None

    """
    if not award_criterion_number_weight_data:
        logger.warning("No Award Criterion Number Weight data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in award_criterion_number_weight_data["tender"]["lots"]:
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
        "Merged Award Criterion Number Weight data for %d lots",
        len(award_criterion_number_weight_data["tender"]["lots"]),
    )
