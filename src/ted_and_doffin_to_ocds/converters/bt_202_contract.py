# converters/bt_202_Contract.py

import uuid
from lxml import etree


def parse_contract_modification_summary(xml_content):
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

    contract_modifications = root.xpath(
        "//efac:ContractModification",
        namespaces=namespaces,
    )

    for modification in contract_modifications:
        contract_id = modification.xpath(
            "efac:Change/efac:ChangedSection/efbc:ChangedSectionIdentifier/text()",
            namespaces=namespaces,
        )
        change_description = modification.xpath(
            "efac:Change/efbc:ChangeDescription/text()",
            namespaces=namespaces,
        )

        if contract_id and change_description:
            contract = {
                "id": contract_id[0],
                "amendments": [
                    {"id": str(uuid.uuid4()), "description": change_description[0]},
                ],
            }

            # Find the corresponding LotResult
            lot_results = root.xpath(
                f"//efac:noticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id[0]}']",
                namespaces=namespaces,
            )
            if len(lot_results) == 1:
                award_id = lot_results[0].xpath(
                    "cbc:ID[@schemeName='result']/text()",
                    namespaces=namespaces,
                )
                if award_id:
                    contract["awardID"] = award_id[0]
            elif len(lot_results) > 1:
                contract["awardIDs"] = [
                    result.xpath(
                        "cbc:ID[@schemeName='result']/text()",
                        namespaces=namespaces,
                    )[0]
                    for result in lot_results
                    if result.xpath(
                        "cbc:ID[@schemeName='result']/text()",
                        namespaces=namespaces,
                    )
                ]

            result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_contract_modification_summary(release_json, modification_data):
    if not modification_data:
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in modification_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_amendments = existing_contract.setdefault("amendments", [])
            for new_amendment in new_contract["amendments"]:
                existing_amendment = next(
                    (
                        amendment
                        for amendment in existing_amendments
                        if amendment["id"] == new_amendment["id"]
                    ),
                    None,
                )
                if existing_amendment:
                    existing_amendment.update(new_amendment)
                else:
                    existing_amendments.append(new_amendment)
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
            if "awardIDs" in new_contract:
                existing_contract["awardIDs"] = new_contract["awardIDs"]
        else:
            existing_contracts.append(new_contract)
