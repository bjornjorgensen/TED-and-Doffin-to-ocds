# converters/bt_162_Tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

USER_CHARGE_TITLE = "The estimated revenue coming from the users of the concession (e.g. fees and fines)."


def parse_concession_revenue_user(xml_content: str | bytes) -> dict | None:
    """
    Parse user concession revenue from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing tender information

    Returns:
        Optional[Dict]: Dictionary containing contract information, or None if no data found
        The structure follows the format:
        {
            "contracts": [
                {
                    "id": str,
                    "implementation": {
                        "charges": [
                            {
                                "id": "user",
                                "title": str,
                                "estimatedValue": {
                                    "amount": float,
                                    "currency": str
                                },
                                "paidBy": "user"
                            }
                        ]
                    },
                    "awardID": str  # Optional
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

    # Process lot tenders
    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        revenue = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenueUserAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenueUserAmount/@currencyID",
            namespaces=namespaces,
        )

        if tender_id and revenue and currency:
            # Find corresponding contract
            contract = root.xpath(
                f"//efac:NoticeResult/efac:SettledContract[efac:LotTender/cbc:ID[@schemeName='tender']='{tender_id[0]}']",
                namespaces=namespaces,
            )
            if contract:
                contract_id = contract[0].xpath(
                    "cbc:ID[@schemeName='contract']/text()",
                    namespaces=namespaces,
                )
                if contract_id:
                    contract_data = {
                        "id": contract_id[0],
                        "implementation": {
                            "charges": [
                                {
                                    "id": "user",
                                    "title": USER_CHARGE_TITLE,
                                    "estimatedValue": {
                                        "amount": float(revenue[0]),
                                        "currency": currency[0],
                                    },
                                    "paidBy": "user",
                                }
                            ]
                        },
                    }

                    # Add award ID if mapping exists
                    if contract_id[0] in contract_awards:
                        contract_data["awardID"] = contract_awards[contract_id[0]]

                    result["contracts"].append(contract_data)

    return result if result["contracts"] else None


def merge_concession_revenue_user(
    release_json: dict, concession_revenue_data: dict | None
) -> None:
    """
    Merge user concession revenue data into the release JSON.

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

    logger.info(
        "Merged Concession Revenue User data for %d contracts",
        len(concession_revenue_data["contracts"]),
    )
