# converters/BT_3202_Contract.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_tender_id(xml_content):
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

    result = {"parties": [], "awards": [], "contracts": []}

    notice_results = root.xpath("//efac:NoticeResult", namespaces=namespaces)

    for notice_result in notice_results:
        settled_contracts = notice_result.xpath(
            "efac:SettledContract", namespaces=namespaces,
        )

        for settled_contract in settled_contracts:
            contract_id = settled_contract.xpath(
                "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces,
            )[0]
            lot_tender_id = settled_contract.xpath(
                "efac:LotTender/cbc:ID[@schemeName='tender']/text()",
                namespaces=namespaces,
            )[0]

            contract = {"id": contract_id, "relatedBids": [lot_tender_id]}
            result["contracts"].append(contract)

            lot_tender = notice_result.xpath(
                f"efac:LotTender[cbc:ID[@schemeName='tender']/text()='{lot_tender_id}']",
                namespaces=namespaces,
            )[0]
            tendering_party_id = lot_tender.xpath(
                "efac:TenderingParty/cbc:ID[@schemeName='tendering-party']/text()",
                namespaces=namespaces,
            )[0]

            tendering_party = notice_result.xpath(
                f"efac:TenderingParty[cbc:ID[@schemeName='tendering-party']/text()='{tendering_party_id}']",
                namespaces=namespaces,
            )[0]
            tenderers = tendering_party.xpath("efac:Tenderer", namespaces=namespaces)

            for tenderer in tenderers:
                organization_id = tenderer.xpath(
                    "cbc:ID[@schemeName='organization']/text()", namespaces=namespaces,
                )[0]

                party = {"id": organization_id, "roles": ["supplier"]}
                result["parties"].append(party)

                lot_results = notice_result.xpath(
                    f"efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']",
                    namespaces=namespaces,
                )

                for lot_result in lot_results:
                    award_id = lot_result.xpath(
                        "cbc:ID[@schemeName='result']/text()", namespaces=namespaces,
                    )[0]
                    lot_id = lot_result.xpath(
                        "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                        namespaces=namespaces,
                    )[0]

                    award = {
                        "id": award_id,
                        "suppliers": [{"id": organization_id}],
                        "relatedLots": [lot_id],
                    }
                    result["awards"].append(award)

    return result


def merge_contract_tender_id(release_json, contract_tender_id_data):
    if not contract_tender_id_data:
        logger.warning("No Contract Tender ID data to merge")
        return

    # Merge parties
    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for new_party in contract_tender_id_data["parties"]:
        if new_party["id"] in existing_parties:
            existing_parties[new_party["id"]]["roles"] = list(
                set(
                    existing_parties[new_party["id"]].get("roles", [])
                    + new_party["roles"],
                ),
            )
        else:
            existing_parties[new_party["id"]] = new_party
    release_json["parties"] = list(existing_parties.values())

    # Merge awards
    existing_awards = {award["id"]: award for award in release_json.get("awards", [])}
    for new_award in contract_tender_id_data["awards"]:
        if new_award["id"] in existing_awards:
            existing_award = existing_awards[new_award["id"]]
            existing_award["suppliers"] = list(
                {
                    supplier["id"]: supplier
                    for supplier in existing_award.get("suppliers", [])
                    + new_award["suppliers"]
                }.values(),
            )
            existing_award["relatedLots"] = list(
                set(existing_award.get("relatedLots", []) + new_award["relatedLots"]),
            )
        else:
            existing_awards[new_award["id"]] = new_award
    release_json["awards"] = list(existing_awards.values())

    # Merge contracts
    existing_contracts = {
        contract["id"]: contract for contract in release_json.get("contracts", [])
    }
    for new_contract in contract_tender_id_data["contracts"]:
        if new_contract["id"] in existing_contracts:
            existing_contracts[new_contract["id"]]["relatedBids"] = list(
                set(
                    existing_contracts[new_contract["id"]].get("relatedBids", [])
                    + new_contract["relatedBids"],
                ),
            )
        else:
            existing_contracts[new_contract["id"]] = new_contract
    release_json["contracts"] = list(existing_contracts.values())

    logger.info(
        f"Merged Contract Tender ID data for {len(contract_tender_id_data['contracts'])} contracts",
    )
