# converters/bt_734_LotsGroup.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_lots_group_award_criterion_name(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse BT-734: Award criterion name for lot groups.

    This field maps to the same AwardCriterion objects as created for BT-539-LotsGroup,
    BT-540-LotsGroup, BT-541-LotsGroup-FixedNumber, BT-541-LotsGroup-ThresholdNumber,
    BT-541-LotsGroup-WeightNumber, BT-5421-LotsGroup, BT-5422-LotsGroup and BT-5423-LotsGroup.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lotGroups": [
                        {
                            "id": str,
                            "awardCriteria": {
                                "criteria": [
                                    {
                                        "name": str
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lotGroups": []}}

        lot_groups = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']",
            namespaces=NAMESPACES,
        )

        for lot_group in lot_groups:
            group_id = lot_group.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            criteria = lot_group.xpath(
                ".//cac:SubordinateAwardingCriterion/cbc:Name/text()",
                namespaces=NAMESPACES,
            )

            if criteria:
                criteria_list = []
                for criterion_name in criteria:
                    name = criterion_name.strip()
                    logger.info(
                        "Found award criterion '%s' for lot group %s", name, group_id
                    )
                    criteria_list.append({"name": name})

                group_data = {
                    "id": group_id,
                    "awardCriteria": {"criteria": criteria_list},
                }
                result["tender"]["lotGroups"].append(group_data)

        return result if result["tender"]["lotGroups"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing award criterion names")
        return None


def merge_lots_group_award_criterion_name(
    release_json: dict, criterion_data: dict | None
) -> None:
    """
    Merge award criterion name data into the release JSON.

    Updates or adds award criteria for lot groups, handling existing criteria appropriately.

    Args:
        release_json: Main OCDS release JSON to update
        criterion_data: Award criterion data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lotGroups array if needed
        - Updates existing lot groups' awardCriteria
        - Handles duplicate criteria by checking names
    """
    if not criterion_data:
        logger.warning("No Award Criterion Name data for lot groups to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_groups = tender.setdefault("lotGroups", [])

    for new_group in criterion_data["tender"]["lotGroups"]:
        existing_group = next(
            (group for group in existing_groups if group["id"] == new_group["id"]), None
        )
        if existing_group:
            existing_criteria = existing_group.setdefault(
                "awardCriteria", {}
            ).setdefault("criteria", [])
            for new_criterion in new_group["awardCriteria"]["criteria"]:
                if not any(
                    c.get("name") == new_criterion["name"] for c in existing_criteria
                ):
                    existing_criteria.append(new_criterion)
        else:
            existing_groups.append(new_group)

    logger.info(
        "Merged Award Criterion Name data for %d lot groups",
        len(criterion_data["tender"]["lotGroups"]),
    )
