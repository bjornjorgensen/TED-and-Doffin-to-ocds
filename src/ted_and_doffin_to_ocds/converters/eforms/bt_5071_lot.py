# converters/bt_5071_lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_country_subdivision(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse place performance country subdivision (BT-5071) from XML content."""
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"items": []}}

        # Get all lots using exact BT-5071 path
        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces={
                "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
                "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            },
        )

        found_regions = False
        for lot in lots:
            try:
                lot_id = lot.xpath(
                    "cbc:ID/text()",
                    namespaces={
                        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                    },
                )[0]

                # Get regions using exact path from specification
                regions = lot.xpath(
                    "cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode/text()",
                    namespaces={
                        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
                        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
                    },
                )

                if regions:
                    found_regions = True
                    addresses = [{"region": code} for code in regions if code.strip()]
                    if addresses:
                        result["tender"]["items"].append(
                            {
                                "id": str(len(result["tender"]["items"]) + 1),
                                "relatedLot": lot_id,
                                "deliveryAddresses": addresses,
                            }
                        )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot data: %s", e)
                continue

        if found_regions:
            return result

    except Exception:
        logger.exception("Error parsing place performance country subdivision")
        return None
    else:
        return None


def merge_place_performance_country_subdivision(
    release_json: dict[str, Any], subdivision_data: dict[str, Any] | None
) -> None:
    """Merge place performance country subdivision data into the release JSON."""
    if not subdivision_data:
        logger.debug("No place performance country subdivision data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in subdivision_data["tender"]["items"]:
        if "relatedLot" not in new_item:
            logger.warning("Skipping item without relatedLot: %s", new_item)
            continue

        try:
            existing_item = next(
                (
                    item
                    for item in existing_items
                    if "relatedLot" in item
                    and item["relatedLot"] == new_item["relatedLot"]
                ),
                None,
            )

            if existing_item:
                existing_addresses = existing_item.setdefault("deliveryAddresses", [])
                for new_address in new_item["deliveryAddresses"]:
                    # Find address without region or add new one
                    existing_address = next(
                        (addr for addr in existing_addresses if "region" not in addr),
                        None,
                    )
                    if existing_address:
                        existing_address["region"] = new_address["region"]
                    else:
                        existing_addresses.append(new_address)
            else:
                existing_items.append(new_item)

        except (IndexError, AttributeError) as e:
            logger.warning("Skipping item due to error: %s", e)
            continue

    logger.info(
        "Merged place performance country subdivision data for %d items",
        len(subdivision_data["tender"]["items"]),
    )
