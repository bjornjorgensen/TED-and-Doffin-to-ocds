# converters/opt_071_lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

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


def parse_quality_target_code(xml_content):
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
            "No quality target code data found. Skipping parse_quality_target_code."
        )
        return None

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        customer_services = lot.xpath(
            "cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='customer-service']/cbc:ExecutionRequirementCode/text()",
            namespaces=namespaces,
        )

        if customer_services:
            lot_data = {
                "id": lot_id,
                "contractTerms": {
                    "customerServices": [
                        {
                            "type": service,
                            "name": CUSTOMER_SERVICE_CODES.get(service, "Unknown"),
                        }
                        for service in customer_services
                    ]
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_quality_target_code(release_json, quality_target_code_data):
    if not quality_target_code_data:
        logger.info("No quality target code data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in quality_target_code_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_contract_terms = existing_lot.setdefault("contractTerms", {})
            existing_customer_services = existing_contract_terms.setdefault(
                "customerServices", []
            )
            existing_customer_services.extend(
                new_lot["contractTerms"]["customerServices"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged quality target code data for %d lots",
        len(quality_target_code_data["tender"]["lots"]),
    )
