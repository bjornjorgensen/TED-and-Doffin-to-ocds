# converters/opt_071_lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

CUSTOMER_SERVICE_CODES = {
    "assistance": "Assistance for persons with reduced mobility",
    "cancel": "Cancellations",
    "clean": "Cleanliness of rolling stock and station facilities",
    "complaint": "Complaint handling",
    "info": "Information",
    "other": "Other",
    "reliability": "Punctuality and reliability",
    "sat-surv": "Customer satisfaction survey",
    "ticket": "Ticketing",
}


def parse_quality_target_code(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse quality target code information (OPT-071) from XML content.

    Gets customer service codes for each lot and maps them to
    corresponding lot's contractTerms.customerServices array.

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

                service_codes = lot.xpath(
                    "cac:TenderingTerms/cac:ContractExecutionRequirement"
                    "[cbc:ExecutionRequirementCode/@listName='customer-service']"
                    "/cbc:ExecutionRequirementCode/text()",
                    namespaces=NAMESPACES,
                )

                if service_codes:
                    customer_services = []
                    for code in service_codes:
                        if code.strip():
                            service = {
                                "type": code,
                                "name": CUSTOMER_SERVICE_CODES.get(code, "Unknown"),
                            }
                            customer_services.append(service)

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
        logger.exception("Error parsing quality target codes")
        return None

    return None


def merge_quality_target_code(
    release_json: dict[str, Any], target_code_data: dict[str, Any] | None
) -> None:
    """Merge quality target code information into the release JSON.

    Updates or creates lots with customer service information.
    Preserves existing lot data while adding/updating services.

    Args:
        release_json: The target release JSON to update
        target_code_data: The source data containing service codes to merge

    Returns:
        None

    """
    if not target_code_data:
        logger.warning("No quality target code data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in target_code_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            contract_terms = existing_lot.setdefault("contractTerms", {})
            customer_services = contract_terms.setdefault("customerServices", [])
            for service in new_lot["contractTerms"]["customerServices"]:
                if service not in customer_services:
                    customer_services.append(service)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged quality target codes for %d lots",
        len(target_code_data["tender"]["lots"]),
    )
