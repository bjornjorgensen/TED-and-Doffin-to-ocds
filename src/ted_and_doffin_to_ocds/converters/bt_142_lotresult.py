# converters/bt_142_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_winner_chosen(xml_content):
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

    result = {"awards": [], "tender": {"lots": []}}

    status_code_mapping = {
        "clos-nw": "No winner was chosen and the competition is closed.",
        "open-nw": "The winner was not yet chosen, but the competition is still ongoing.",
        "selec-w": "At least one winner was chosen.",
    }

    lot_results = root.xpath(
        "//efac:noticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        result_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        tender_result_code = lot_result.xpath(
            "cbc:TenderResultCode[@listName='winner-selection-status']/text()",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if result_id and tender_result_code and lot_id:
            result_id = result_id[0]
            tender_result_code = tender_result_code[0]
            lot_id = lot_id[0]

            if tender_result_code == "open-nw":
                result["tender"]["lots"].append({"id": lot_id, "status": "active"})
            elif tender_result_code == "selec-w":
                award = {
                    "id": result_id,
                    "status": "active",
                    "statusDetails": status_code_mapping.get(
                        tender_result_code,
                        "Unknown",
                    ),
                    "relatedLots": [lot_id],
                }
                result["awards"].append(award)
            # We're not creating awards for 'clos-nw' case as per the original requirements

    return result if (result["awards"] or result["tender"]["lots"]) else None


def merge_winner_chosen(release_json, winner_chosen_data):
    if not winner_chosen_data:
        logger.warning("No winner chosen data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])
    for new_award in winner_chosen_data["awards"]:
        existing_award = next(
            (a for a in existing_awards if a["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award.update(new_award)
        else:
            existing_awards.append(new_award)

    # Remove any existing awards that are not in the new data
    release_json["awards"] = [
        award
        for award in existing_awards
        if any(
            new_award["id"] == award["id"] for new_award in winner_chosen_data["awards"]
        )
    ]

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    for new_lot in winner_chosen_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.update(new_lot)
        else:
            existing_lots.append(new_lot)
    logger.info(
        f"Merged winner chosen data for {len(winner_chosen_data['awards'])} awards and {len(winner_chosen_data['tender']['lots'])} lots",
    )
