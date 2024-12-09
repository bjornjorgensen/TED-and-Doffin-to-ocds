# converters/bt_543_LotsGroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criteria_weighting_description_lotsgroup(
    xml_content: str | bytes,
) -> dict | None:
    """Parse award criteria weighting descriptions from XML content for lot groups.

    Extracts weighting descriptions from award criteria for each lot group from the XML.
    The descriptions are found in CalculationExpression elements under AwardingCriterion.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender lot groups with their award criteria
        weighting descriptions, or None if no relevant data found. Structure:
        {
            "tender": {
                "lotGroups": [
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

    result = {"tender": {"lotGroups": []}}

    lot_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lot_group in lot_groups:
        lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        weighting_descriptions = lot_group.xpath(
            ".//cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cbc:CalculationExpression/text()",
            namespaces=namespaces,
        )

        if weighting_descriptions:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {"weightingDescription": weighting_descriptions[0]},
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criteria_weighting_description_lotsgroup(
    release_json: dict, award_criteria_data: dict | None
) -> None:
    """Merge award criteria weighting descriptions into the release JSON for lot groups.

    Takes the parsed weighting descriptions and merges them into the appropriate lot groups
    in the release JSON.

    Args:
        release_json: The target release JSON to update
        award_criteria_data: The source data containing weighting descriptions
            to merge, in the format returned by parse_award_criteria_weighting_description_lotsgroup()

    Returns:
        None

    """
    if not award_criteria_data:
        logger.warning(
            "No award criteria weighting description data to merge for lot groups"
        )
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_lot_group in award_criteria_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (
                group
                for group in existing_lot_groups
                if group["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            existing_lot_group.setdefault("awardCriteria", {}).update(
                new_lot_group["awardCriteria"]
            )
        else:
            existing_lot_groups.append(new_lot_group)

    logger.info(
        "Merged award criteria weighting description data for %d lot groups",
        len(award_criteria_data["tender"]["lotGroups"]),
    )
