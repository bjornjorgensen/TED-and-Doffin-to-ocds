# converters/bt_709_LotResult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_maximum_value(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the framework maximum value (BT-709) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed framework maximum value data in OCDS format, or None if no data found.
        Format:
        {
            "awards": [
                {
                    "id": "RES-0001",
                    "maximumValue": {
                        "amount": 5000,
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
        max_value = lot_result.xpath(
            "efac:FrameworkAgreementValues/cbc:MaximumValueAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_result.xpath(
            "efac:FrameworkAgreementValues/cbc:MaximumValueAmount/@currencyID",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if award_id and max_value and currency and lot_id:
            award_data = {
                "id": award_id[0],
                "maximumValue": {
                    "amount": float(max_value[0]),
                    "currency": currency[0],
                },
                "relatedLots": [lot_id[0]],
            }
            result["awards"].append(award_data)

    return result if result["awards"] else None


def merge_framework_maximum_value(
    release_json: dict[str, Any],
    framework_max_value_data: dict[str, Any] | None,
) -> None:
    """Merge framework maximum value data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        framework_max_value_data: The framework maximum value data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not framework_max_value_data:
        logger.warning("No framework maximum value data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in framework_max_value_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award["maximumValue"] = new_award["maximumValue"]
            existing_award.setdefault("relatedLots", []).extend(
                new_award["relatedLots"],
            )
            existing_award["relatedLots"] = list(
                set(existing_award["relatedLots"]),
            )  # Remove duplicates
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged framework maximum value data for %d awards",
        len(framework_max_value_data["awards"]),
    )
