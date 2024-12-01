import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_threshold_number(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criterion threshold numbers from XML content.

    Extracts threshold numbers associated with award criteria for each lot from the XML.
    The numbers are found under the SubordinateAwardingCriterion elements with
    ParameterCode listName='number-threshold'.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lots with their award criteria
        threshold numbers, or None if no relevant data found. Structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "awardCriteria": {
                            "criteria": [
                                {
                                    "numbers": [{"number": float}]
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

        threshold_numbers = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efbc:ParameterNumeric/text()",
            namespaces=namespaces,
        )

        if threshold_numbers:
            lot_data = {
                "id": lot_id,
                "awardCriteria": {
                    "criteria": [
                        {
                            "numbers": [
                                {"number": float(number)}
                                for number in threshold_numbers
                            ],
                        },
                    ],
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criterion_threshold_number(
    release_json: dict, award_criterion_threshold_number_data: dict | None
) -> None:
    """Merge award criterion threshold number data into the release JSON.

    Takes the parsed threshold number data and merges it into the appropriate lots
    in the release JSON. For each lot, updates or adds award criteria numbers
    while avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        award_criterion_threshold_number_data: The source data containing threshold numbers
            to merge, in the format returned by parse_award_criterion_threshold_number()

    Returns:
        None
    """
    if not award_criterion_threshold_number_data:
        logger.warning("No Award Criterion Threshold Number data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in award_criterion_threshold_number_data["tender"]["lots"]:
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
        "Merged Award Criterion Threshold Number data for %d lots",
        len(award_criterion_threshold_number_data["tender"]["lots"]),
    )
