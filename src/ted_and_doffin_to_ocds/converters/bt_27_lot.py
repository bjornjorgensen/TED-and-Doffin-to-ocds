import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_estimated_value(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse the estimated value for each procurement lot from XML content.

    Args:
        xml_content: XML string or bytes containing procurement lots

    Returns:
        Dictionary containing lot values or None if no lots found:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
                        "value": {
                            "amount": 250000,
                            "currency": "EUR"
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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        estimated_value = lot.xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount/text()",
            namespaces=namespaces,
        )
        currency = lot.xpath(
            "cac:ProcurementProject/cac:RequestedTenderTotal/cbc:EstimatedOverallContractAmount/@currencyID",
            namespaces=namespaces,
        )

        if estimated_value and currency:
            lot_data = {
                "id": lot_id,
                "value": {"amount": float(estimated_value[0]), "currency": currency[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_estimated_value(
    release_json: dict[str, Any], lot_estimated_value_data: dict[str, Any] | None
) -> None:
    """Merge lot estimated value data into existing release JSON.

    Args:
        release_json: Target release JSON to merge into
        lot_estimated_value_data: Source lot value data to merge from

    Returns:
        None. Modifies release_json in place.
        Logs warning if no lot data to merge.
        Logs info about number of lots merged.

    """
    if not lot_estimated_value_data:
        logger.warning("No Lot Estimated Value data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_estimated_value_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["value"] = new_lot["value"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Lot Estimated Value data for %(num_lots)d lots",
        {"num_lots": len(lot_estimated_value_data["tender"]["lots"])},
    )
