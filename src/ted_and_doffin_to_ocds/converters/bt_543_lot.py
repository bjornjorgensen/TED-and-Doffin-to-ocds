# converters/bt_543_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criteria_weighting_description_lot(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criteria weighting descriptions from XML content.

    Extracts weighting descriptions from award criteria for each lot from the XML.
    The descriptions are found in CalculationExpression elements under AwardingCriterion.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lots with their award criteria
        weighting descriptions, or None if no relevant data found. Structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "awardCriteria": {
                            "weightingDescription": str
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

        weighting_descriptions = lot.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cbc:CalculationExpression/text()",
            namespaces=namespaces,
        )

        if weighting_descriptions:
            lot_data = {
                "id": lot_id,
                "awardCriteria": {"weightingDescription": weighting_descriptions[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criteria_weighting_description_lot(
    release_json: dict, award_criteria_data: dict | None
) -> None:
    """Merge award criteria weighting descriptions into the release JSON.

    Takes the parsed weighting descriptions and merges them into the appropriate lots
    in the release JSON.

    Args:
        release_json: The target release JSON to update
        award_criteria_data: The source data containing weighting descriptions
            to merge, in the format returned by parse_award_criteria_weighting_description_lot()

    Returns:
        None
    """
    if not award_criteria_data:
        logger.warning("No award criteria weighting description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in award_criteria_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("awardCriteria", {}).update(
                new_lot["awardCriteria"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged award criteria weighting description data for %d lots",
        len(award_criteria_data["tender"]["lots"]),
    )
