# converters/opt_072_lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_quality_target_description(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='customer-service']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No quality target description data found. Skipping parse_quality_target_description."
        )
        return None

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        customer_services = lot.xpath(
            "cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='customer-service']",
            namespaces=namespaces,
        )

        if customer_services:
            lot_data = {"id": lot_id, "contractTerms": {"customerServices": []}}
            for service in customer_services:
                description = service.xpath(
                    "cbc:Description/text()", namespaces=namespaces
                )
                if description:
                    lot_data["contractTerms"]["customerServices"].append(
                        {"description": description[0]}
                    )
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_quality_target_description(release_json, quality_target_description_data):
    if not quality_target_description_data:
        logger.info("No quality target description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in quality_target_description_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_contract_terms = existing_lot.setdefault("contractTerms", {})
            existing_customer_services = existing_contract_terms.setdefault(
                "customerServices", []
            )

            for new_service in new_lot["contractTerms"]["customerServices"]:
                if existing_customer_services:
                    existing_customer_services[0].update(new_service)
                else:
                    existing_customer_services.append(new_service)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged quality target description data for %d lots",
        len(quality_target_description_data["tender"]["lots"]),
    )
