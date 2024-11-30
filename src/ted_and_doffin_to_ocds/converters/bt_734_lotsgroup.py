# converters/bt_734_LotsGroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_name_lotsgroup(xml_content):
    """
    Parse the XML content to extract the award criterion name for each lots group.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed award criterion name data for lots groups.
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

    lots_groups = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
        namespaces=namespaces,
    )

    for lots_group in lots_groups:
        group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lots_group.xpath(
            ".//cac:SubordinateAwardingCriterion/cbc:Name/text()",
            namespaces=namespaces,
        )

        if criteria:
            group_data = {
                "id": group_id,
                "awardCriteria": {"criteria": [{"name": name} for name in criteria]},
            }
            result["tender"]["lotGroups"].append(group_data)

    return result if result["tender"]["lotGroups"] else None


def merge_award_criterion_name_lotsgroup(release_json, award_criterion_data) -> None:
    """
    Merge the parsed award criterion name data for lots groups into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        award_criterion_data (dict): The parsed award criterion name data for lots groups to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not award_criterion_data:
        logger.warning("No Award Criterion Name data for lots groups to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lot_groups = tender.setdefault("lotGroups", [])

    for new_group in award_criterion_data["tender"]["lotGroups"]:
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
                existing_criterion = next(
                    (
                        c
                        for c in existing_criteria
                        if c.get("name") == new_criterion["name"]
                    ),
                    None,
                )
                if existing_criterion:
                    existing_criterion.update(new_criterion)
                else:
                    existing_criteria.append(new_criterion)
        else:
            existing_lot_groups.append(new_group)

    logger.info(
        "Merged Award Criterion Name data for %d lots groups",
        len(award_criterion_data["tender"]["lotGroups"]),
    )
