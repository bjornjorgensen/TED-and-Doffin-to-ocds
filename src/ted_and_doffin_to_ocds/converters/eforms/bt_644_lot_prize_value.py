# converters/bt_644_Lot_Prize_Value.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_prize_value(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the prize value (BT-644) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed prize value data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
                        "designContest": {
                            "prizes": {
                                "details": [
                                    {
                                        "id": "0",
                                        "value": {
                                            "amount": 5000,
                                            "currency": "EUR"
                                        }
                                    }
                                ]
                            }
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        prizes = lot.xpath(
            "cac:TenderingTerms/cac:AwardingTerms/cac:Prize",
            namespaces=namespaces,
        )

        if prizes:
            lot_data = {"id": lot_id, "designContest": {"prizes": {"details": []}}}

            for i, prize in enumerate(prizes):
                value_amount = prize.xpath(
                    "cbc:ValueAmount/text()",
                    namespaces=namespaces,
                )
                currency = prize.xpath(
                    "cbc:ValueAmount/@currencyID",
                    namespaces=namespaces,
                )

                if value_amount and currency:
                    prize_data = {
                        "id": str(i),
                        "value": {
                            "amount": float(value_amount[0]),
                            "currency": currency[0],
                        },
                    }
                    lot_data["designContest"]["prizes"]["details"].append(prize_data)

            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_prize_value(
    release_json: dict[str, Any],
    lot_prize_value_data: dict[str, Any] | None,
) -> None:
    """Merge lot prize value data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        lot_prize_value_data: The lot prize value data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not lot_prize_value_data:
        logger.warning("No lot prize value data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_prize_value_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            design_contest = existing_lot.setdefault("designContest", {})
            prizes = design_contest.setdefault("prizes", {})
            details = prizes.setdefault("details", [])

            for new_prize in new_lot["designContest"]["prizes"]["details"]:
                existing_prize = next(
                    (prize for prize in details if prize["id"] == new_prize["id"]),
                    None,
                )
                if existing_prize:
                    existing_prize.update(new_prize)
                else:
                    details.append(new_prize)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged lot prize value data for %d lots",
        len(lot_prize_value_data["tender"]["lots"]),
    )
