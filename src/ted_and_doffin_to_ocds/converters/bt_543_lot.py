# converters/bt_543_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_award_criteria_complicated(xml_content):
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
        calculation_expression = lot.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cbc:CalculationExpression/text()",
            namespaces=namespaces,
        )

        if calculation_expression:
            lot_data = {
                "id": lot_id,
                "awardCriteria": {"weightingDescription": calculation_expression[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_award_criteria_complicated(release_json, award_criteria_data):
    if not award_criteria_data:
        logger.warning("No award criteria complicated data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

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
        "Merged award criteria complicated data for %d lots",
        len(award_criteria_data["tender"]["lots"]),
    )
