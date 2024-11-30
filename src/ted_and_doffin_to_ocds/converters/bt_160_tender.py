# converters/bt_160_Tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_concession_revenue_buyer(xml_content):
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

    lot_tenders = root.xpath(
        "//efac:noticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        revenue_buyer = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenuebuyerAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenuebuyerAmount/@currencyID",
            namespaces=namespaces,
        )

        if tender_id and revenue_buyer and currency:
            settled_contract = root.xpath(
                f"//efac:noticeResult/efac:SettledContract[efac:LotTender/cbc:ID[@schemeName='tender'] = '{tender_id[0]}']",
                namespaces=namespaces,
            )

            if settled_contract:
                contract_id = settled_contract[0].xpath(
                    "cbc:ID[@schemeName='contract']/text()",
                    namespaces=namespaces,
                )
                lot_result = root.xpath(
                    f"//efac:noticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id[0]}']",
                    namespaces=namespaces,
                )

                if lot_result:
                    award_id = lot_result[0].xpath(
                        "cbc:ID[@schemeName='result']/text()",
                        namespaces=namespaces,
                    )

                    contract = {
                        "id": contract_id[0],
                        "awardID": award_id[0] if award_id else None,
                        "implementation": {
                            "charges": [
                                {
                                    "id": "government",
                                    "title": "The estimated revenue coming from the buyer who granted the concession (e.g. prizes and payments).",
                                    "estimatedValue": {
                                        "amount": float(revenue_buyer[0]),
                                        "currency": currency[0],
                                    },
                                    "paidBy": "government",
                                },
                            ],
                        },
                    }
                    result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_concession_revenue_buyer(release_json, concession_revenue_buyer_data) -> None:
    if not concession_revenue_buyer_data:
        logger.warning("No Concession Revenue buyer data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in concession_revenue_buyer_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_implementation = existing_contract.setdefault("implementation", {})
            existing_charges = existing_implementation.setdefault("charges", [])
            existing_charges.extend(new_contract["implementation"]["charges"])
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Concession Revenue buyer data for %d contracts",
        len(concession_revenue_buyer_data["contracts"]),
    )
