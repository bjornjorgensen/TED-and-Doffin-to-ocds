# converters/BT_733_LotsGroup.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lots_group_award_criteria_order_justification(xml_content):
    """
    Parse the XML content to extract award criteria order justification for lot groups.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed award criteria order justification data for lot groups.
        None: If no relevant data is found.
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
        order_justification = lot_group.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cbc:Description/text()",
            namespaces=namespaces,
        )

        if order_justification:
            lot_group_data = {
                "id": lot_group_id,
                "awardCriteria": {"orderRationale": order_justification[0].strip()},
            }
            result["tender"]["lotGroups"].append(lot_group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_lots_group_award_criteria_order_justification(
    release_json, lots_group_award_criteria_order_justification_data
):
    """
    Merge the parsed award criteria order justification data for lot groups into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lots_group_award_criteria_order_justification_data (dict): The parsed award criteria order justification data for lot groups to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lots_group_award_criteria_order_justification_data:
        logger.warning("No lot group award criteria order justification data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "lotGroups" not in release_json["tender"]:
        release_json["tender"]["lotGroups"] = []

    for new_lot_group in lots_group_award_criteria_order_justification_data["tender"][
        "lotGroups"
    ]:
        existing_lot_group = next(
            (
                lg
                for lg in release_json["tender"]["lotGroups"]
                if lg["id"] == new_lot_group["id"]
            ),
            None,
        )
        if existing_lot_group:
            if "awardCriteria" not in existing_lot_group:
                existing_lot_group["awardCriteria"] = {}
            existing_lot_group["awardCriteria"]["orderRationale"] = new_lot_group[
                "awardCriteria"
            ]["orderRationale"]
        else:
            release_json["tender"]["lotGroups"].append(new_lot_group)

    logger.info(
        f"Merged award criteria order justification data for {len(lots_group_award_criteria_order_justification_data['tender']['lotGroups'])} lot groups"
    )
