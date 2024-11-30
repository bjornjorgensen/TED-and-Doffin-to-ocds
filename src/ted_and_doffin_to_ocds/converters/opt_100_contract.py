# converters/opt_100_contract.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_notice_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    # Check if the relevant XPath exists
    relevant_xpath = (
        "//efac:NoticeResult/efac:SettledContract/cac:NoticeDocumentReference/cbc:ID"
    )
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No framework notice identifier data found. Skipping parse_framework_notice_identifier."
        )
        return None

    result = {"contracts": []}

    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract", namespaces=namespaces
    )
    for contract in settled_contracts:
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces
        )
        notice_ref = contract.xpath(
            "cac:NoticeDocumentReference/cbc:ID", namespaces=namespaces
        )

        if contract_id and notice_ref:
            contract_data = {
                "id": contract_id[0],
                "relatedProcesses": [
                    {
                        "id": "1",
                        "scheme": notice_ref[0].get("schemeName", ""),
                        "identifier": notice_ref[0].text,
                        "relationship": ["framework"],
                    }
                ],
            }

            # Find the corresponding LotResult
            lot_result = root.xpath(
                f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id[0]}']",
                namespaces=namespaces,
            )
            if lot_result:
                award_id = lot_result[0].xpath(
                    "cbc:ID[@schemeName='result']/text()", namespaces=namespaces
                )
                if award_id:
                    contract_data["awardID"] = award_id[0]

            result["contracts"].append(contract_data)

    return result if result["contracts"] else None


def merge_framework_notice_identifier(
    release_json, framework_notice_identifier_data
) -> None:
    if not framework_notice_identifier_data:
        logger.info("No framework notice identifier data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in framework_notice_identifier_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_related_processes = existing_contract.setdefault(
                "relatedProcesses", []
            )
            new_related_process = new_contract["relatedProcesses"][0]
            existing_related_process = next(
                (
                    rp
                    for rp in existing_related_processes
                    if rp["id"] == new_related_process["id"]
                ),
                None,
            )
            if existing_related_process:
                existing_related_process.update(new_related_process)
            else:
                existing_related_processes.append(new_related_process)

            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged framework notice identifier data for %d contracts",
        len(framework_notice_identifier_data["contracts"]),
    )
