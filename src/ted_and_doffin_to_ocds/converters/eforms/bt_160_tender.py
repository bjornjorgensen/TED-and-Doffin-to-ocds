import logging

from lxml import etree

logger = logging.getLogger(__name__)

GOVERNMENT_CHARGE_TITLE = "The estimated revenue coming from the buyer who granted the concession (e.g. prizes and payments)."


def parse_concession_revenue_buyer(xml_content: str | bytes) -> dict | None:
    """Parse concession revenue from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing tender information

    Returns:
        Optional[Dict]: Dictionary containing contract information, or None if no data found
        The structure follows the format:
        {
            "contracts": [
                {
                    "id": str,
                    "awardID": str,
                    "implementation": {
                        "charges": [
                            {
                                "id": "government",
                                "title": str,
                                "estimatedValue": {
                                    "amount": float,
                                    "currency": str
                                },
                                "paidBy": "government"
                            }
                        ]
                    }
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

    result = {"contracts": []}

    # First map contracts to awards
    contract_awards = {}
    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )
    for lot_result in lot_results:
        award_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        contract_id = lot_result.xpath(
            "efac:SettledContract/cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )
        if award_id and contract_id:
            contract_awards[contract_id[0]] = award_id[0]

    # Create mapping between tender IDs and contract IDs
    tender_contracts = {}
    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract",
        namespaces=namespaces,
    )
    for contract in settled_contracts:
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )
        tender_id = contract.xpath(
            "efac:LotTender/cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        if contract_id and tender_id:
            tender_contracts[tender_id[0]] = contract_id[0]

    # Process lot tenders with concession revenue
    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender[efac:ConcessionRevenue/efbc:RevenueBuyerAmount]",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        revenue = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenueBuyerAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenueBuyerAmount/@currencyID",
            namespaces=namespaces,
        )

        if not (tender_id and revenue and currency):
            logger.warning("Incomplete concession revenue data found in tender")
            continue

        # Check if tender is linked to a contract
        if tender_id[0] in tender_contracts:
            contract_id = tender_contracts[tender_id[0]]

            try:
                # Validate the revenue value before creating contract data
                float_revenue = float(revenue[0])

                contract_data = {
                    "id": contract_id,
                    "implementation": {
                        "charges": [
                            {
                                "id": "government",
                                "title": GOVERNMENT_CHARGE_TITLE,
                                "estimatedValue": {
                                    "amount": float_revenue,
                                    "currency": currency[0],
                                },
                                "paidBy": "government",
                            }
                        ]
                    },
                }

                # Add award ID if mapping exists
                if contract_id in contract_awards:
                    contract_data["awardID"] = contract_awards[contract_id]

                result["contracts"].append(contract_data)
            except (ValueError, IndexError) as e:
                logger.warning("Error processing concession revenue data: %s", str(e))
                continue

    return result if result["contracts"] else None


def merge_concession_revenue_buyer(
    release_json: dict, concession_revenue_data: dict | None
) -> None:
    """Merge concession revenue data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        concession_revenue_data (Optional[Dict]): The source data containing contracts
            to be merged. If None, function returns without making changes.

    """
    if not concession_revenue_data:
        return

    existing_contracts = release_json.setdefault("contracts", [])
    for new_contract in concession_revenue_data["contracts"]:
        existing_contract = next(
            (c for c in existing_contracts if c["id"] == new_contract["id"]),
            None,
        )
        if existing_contract:
            existing_implementation = existing_contract.setdefault("implementation", {})
            existing_charges = existing_implementation.setdefault("charges", [])
            existing_charges.extend(new_contract["implementation"]["charges"])
        else:
            existing_contracts.append(new_contract)
