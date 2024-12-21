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


def parse_award_criterion_name(xml_content: str | bytes) -> dict | None:
    """Parse BT-734: The name of the award criterion.

    This field maps to the same AwardCriterion objects as created for BT-539-Lot,
    BT-540-Lot, BT-541-Lot-FixedNumber, BT-541-Lot-ThresholdNumber,
    BT-541-Lot-WeightNumber, BT-5421-Lot, BT-5422-Lot and BT-5423-Lot.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
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
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            criteria = lot.xpath(
                ".//cac:SubordinateAwardingCriterion/cbc:Name/text()",
                namespaces=NAMESPACES,
            )

            if criteria:
                criteria_list = []
                for criterion_name in criteria:
                    name = criterion_name.strip()
                    logger.info("Found award criterion '%s' for lot %s", name, lot_id)
                    criteria_list.append({"name": name})

                lot_data = {"id": lot_id, "awardCriteria": {"criteria": criteria_list}}
                result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing award criterion names")
        return None


def merge_award_criterion_name(release_json: dict, criterion_data: dict | None) -> None:
    """Merge award criterion name data into the release JSON.

    Updates or adds award criteria for lots, handling existing criteria appropriately.

    Args:
        release_json: Main OCDS release JSON to update
        criterion_data: Award criterion data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' awardCriteria
        - Handles duplicate criteria by checking names

    """
    if not criterion_data:
        logger.warning("No Award Criterion Name data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in criterion_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_criteria = existing_lot.setdefault("awardCriteria", {}).setdefault(
                "criteria", []
            )
            for new_criterion in new_lot["awardCriteria"]["criteria"]:
                if not any(
                    c.get("name") == new_criterion["name"] for c in existing_criteria
                ):
                    existing_criteria.append(new_criterion)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Award Criterion Name data for %d lots",
        len(criterion_data["tender"]["lots"]),
    )
