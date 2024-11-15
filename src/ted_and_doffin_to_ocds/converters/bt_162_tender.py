# converters/bt_162_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_concession_revenue_user(xml_content):
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
        revenue_user = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenueUserAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_tender.xpath(
            "efac:ConcessionRevenue/efbc:RevenueUserAmount/@currencyID",
            namespaces=namespaces,
        )

        if tender_id and revenue_user and currency:
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
                                    "id": "user",
                                    "title": "The estimated revenue coming from the users of the concession (e.g. fees and fines).",
                                    "estimatedValue": {
                                        "amount": float(revenue_user[0]),
                                        "currency": currency[0],
                                    },
                                    "paidBy": "user",
                                },
                            ],
                        },
                    }
                    result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_concession_revenue_user(release_json, concession_revenue_user_data):
    if not concession_revenue_user_data:
        logger.warning("No Concession Revenue User data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in concession_revenue_user_data["contracts"]:
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
        "Merged Concession Revenue User data for %d contracts",
        len(concession_revenue_user_data["contracts"]),
    )
