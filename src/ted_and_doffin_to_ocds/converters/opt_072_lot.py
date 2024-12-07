import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_quality_target_description(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse quality target description information (OPT-072) from XML content.

    Maps to the same CustomerServices objects as OPT-071-Lot.
    Gets customer service descriptions for each lot and maps them to the
    corresponding lot's customerServices array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with customer services or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]

                services = lot.xpath(
                    "cac:TenderingTerms/cac:ContractExecutionRequirement"
                    "[cbc:ExecutionRequirementCode/@listName='customer-service']"
                    "/cbc:Description/text()",
                    namespaces=NAMESPACES,
                )

                if services:
                    customer_services = [
                        {"description": desc} for desc in services if desc.strip()
                    ]
                    if customer_services:
                        result["tender"]["lots"].append(
                            {
                                "id": lot_id,
                                "contractTerms": {
                                    "customerServices": customer_services
                                },
                            }
                        )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot data: %s", e)
                continue

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing quality target descriptions")
        return None

    return None


def merge_quality_target_description(
    release_json: dict[str, Any], target_description_data: dict[str, Any] | None
) -> None:
    """
    Merge quality target description information into the release JSON.

    Updates existing customer services with descriptions.
    Preserves existing customer service data while adding/updating descriptions.

    Args:
        release_json: The target release JSON to update
        target_description_data: The source data containing descriptions to merge

    Returns:
        None
    """
    if not target_description_data:
        logger.warning("No quality target description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in target_description_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            contract_terms = existing_lot.setdefault("contractTerms", {})
            existing_services = contract_terms.setdefault("customerServices", [])

            # Update each existing service with new description or add new service
            for new_service in new_lot["contractTerms"]["customerServices"]:
                if existing_services:
                    existing_services[0].update(new_service)
                else:
                    existing_services.append(new_service)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged quality target descriptions for %d lots",
        len(target_description_data["tender"]["lots"]),
    )
