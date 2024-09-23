# converters/BT_734_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criterion_name(xml_content):
    """
    Parse the XML content to extract the award criterion name for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed award criterion name data.
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(
            ".//cac:SubordinateAwardingCriterion/cbc:Name/text()", namespaces=namespaces,
        )

        if criteria:
            lot_data = {
                "id": lot_id,
                "awardCriteria": {"criteria": [{"name": name} for name in criteria]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criterion_name(release_json, award_criterion_data):
    """
    Merge the parsed award criterion name data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        award_criterion_data (dict): The parsed award criterion name data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not award_criterion_data:
        logger.warning("No Award Criterion Name data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in award_criterion_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_criteria = existing_lot.setdefault("awardCriteria", {}).setdefault(
                "criteria", [],
            )
            for new_criterion in new_lot["awardCriteria"]["criteria"]:
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
            existing_lots.append(new_lot)

    logger.info(
        f"Merged Award Criterion Name data for {len(award_criterion_data['tender']['lots'])} lots",
    )
