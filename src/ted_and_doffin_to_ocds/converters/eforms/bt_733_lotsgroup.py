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


def parse_lots_group_award_criteria_order_justification(
    xml_content: str | bytes,
) -> dict | None:
    """Parse BT-733: Award criteria order justification for lot groups.

    Extracts the justification for specifying only order of importance
    rather than specific weights for award criteria.

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
                                "orderRationale": str
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
            lot_group_id = lot_group.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            order_justification = lot_group.xpath(
                "cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cbc:Description/text()",
                namespaces=NAMESPACES,
            )

            if order_justification:
                description = order_justification[0].strip()
                logger.info(
                    "Found award criteria order rationale for lot group %s: %s",
                    lot_group_id,
                    description,
                )
                lot_group_data = {
                    "id": lot_group_id,
                    "awardCriteria": {"orderRationale": description},
                }
                result["tender"]["lotGroups"].append(lot_group_data)

        return result if result["tender"]["lotGroups"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing award criteria order justification")
        return None


def merge_lots_group_award_criteria_order_justification(
    release_json: dict, justification_data: dict | None
) -> None:
    """Merge award criteria order justification data into the release JSON.

    Updates or adds award criteria order rationale for lot groups.

    Args:
        release_json: Main OCDS release JSON to update
        justification_data: Award criteria justification data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lotGroups array if needed
        - Updates existing lot groups' awardCriteria

    """
    if not justification_data:
        logger.warning("No lot group award criteria order justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender.setdefault("lotGroups", [])

    for new_lot_group in justification_data["tender"]["lotGroups"]:
        existing_lot_group = next(
            (lg for lg in tender["lotGroups"] if lg["id"] == new_lot_group["id"]), None
        )
        if existing_lot_group:
            existing_lot_group.setdefault("awardCriteria", {})
            existing_lot_group["awardCriteria"]["orderRationale"] = new_lot_group[
                "awardCriteria"
            ]["orderRationale"]
        else:
            tender["lotGroups"].append(new_lot_group)

    logger.info(
        "Merged award criteria order justification data for %d lot groups",
        len(justification_data["tender"]["lotGroups"]),
    )
