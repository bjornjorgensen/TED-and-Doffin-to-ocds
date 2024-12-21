# converters/bt_733_Lot.py

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


def parse_lot_award_criteria_order_justification(
    xml_content: str | bytes,
) -> dict | None:
    """Parse BT-733: Justification for only indicating award criteria order.

    Extracts the rationale for specifying only the order of importance
    rather than specific weights for award criteria.

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
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            order_justification = lot.xpath(
                "cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cbc:Description/text()",
                namespaces=NAMESPACES,
            )

            if order_justification:
                description = order_justification[0].strip()
                logger.info(
                    "Found award criteria order rationale for lot %s: %s",
                    lot_id,
                    description,
                )
                lot_data = {
                    "id": lot_id,
                    "awardCriteria": {"orderRationale": description},
                }
                result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing award criteria order justification")
        return None


def merge_lot_award_criteria_order_justification(
    release_json: dict, justification_data: dict | None
) -> None:
    """Merge award criteria order justification data into the release JSON.

    Updates or adds award criteria order rationale for lots.

    Args:
        release_json: Main OCDS release JSON to update
        justification_data: Award criteria justification data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' awardCriteria

    """
    if not justification_data:
        logger.warning("No lot award criteria order justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender.setdefault("lots", [])

    for new_lot in justification_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender["lots"] if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_lot.setdefault("awardCriteria", {})
            existing_lot["awardCriteria"]["orderRationale"] = new_lot["awardCriteria"][
                "orderRationale"
            ]
        else:
            tender["lots"].append(new_lot)

    logger.info(
        "Merged award criteria order justification data for %d lots",
        len(justification_data["tender"]["lots"]),
    )
