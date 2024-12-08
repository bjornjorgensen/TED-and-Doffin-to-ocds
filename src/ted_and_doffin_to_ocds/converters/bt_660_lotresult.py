# converters/bt_660_LotResult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_reestimated_value(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the framework re-estimated value (BT-660) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed framework re-estimated value data in OCDS format, or None if no data found.
        Format:
        {
            "awards": [
                {
                    "id": "RES-0001",
                    "estimatedValue": {
                        "amount": 123,
                        "currency": "EUR"
                    },
                    "relatedLots": [
                        "LOT-0001"
                    ]
                }
            ]
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

    result = {"awards": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        award_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        reestimated_value = lot_result.xpath(
            "efac:FrameworkAgreementValues/efbc:ReestimatedValueAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_result.xpath(
            "efac:FrameworkAgreementValues/efbc:ReestimatedValueAmount/@currencyID",
            namespaces=namespaces,
        )
        related_lot = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if award_id and reestimated_value and currency:
            award_data = {
                "id": award_id[0],
                "estimatedValue": {
                    "amount": float(reestimated_value[0]),
                    "currency": currency[0],
                },
            }
            if related_lot:
                award_data["relatedLots"] = [related_lot[0]]
            result["awards"].append(award_data)

    return result if result["awards"] else None


def merge_framework_reestimated_value(
    release_json: dict[str, Any],
    framework_reestimated_value_data: dict[str, Any] | None,
) -> None:
    """Merge framework re-estimated value data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        framework_reestimated_value_data: The framework re-estimated value data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not framework_reestimated_value_data:
        logger.warning("No Framework Re-estimated Value data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in framework_reestimated_value_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award["estimatedValue"] = new_award["estimatedValue"]
            if "relatedLots" in new_award:
                existing_award.setdefault("relatedLots", []).extend(
                    new_award["relatedLots"],
                )
                existing_award["relatedLots"] = list(
                    set(existing_award["relatedLots"]),
                )  # Remove duplicates
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged Framework Re-estimated Value data for %d awards",
        len(framework_reestimated_value_data["awards"]),
    )
