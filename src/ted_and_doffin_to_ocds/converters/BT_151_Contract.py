# converters/BT_151_Contract.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_url(xml_content):
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
    document_id_counter = 1

    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract",
        namespaces=namespaces,
    )

    for contract in settled_contracts:
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )
        contract_url = contract.xpath("cbc:URI/text()", namespaces=namespaces)

        if contract_id and contract_url:
            contract_data = {
                "id": contract_id[0],
                "documents": [
                    {
                        "id": str(document_id_counter),
                        "url": contract_url[0],
                        "documentType": "contractSigned",
                    },
                ],
            }
            document_id_counter += 1

            # Find the corresponding LotResult to get the awardID
            lot_result = root.xpath(
                f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id[0]}']",
                namespaces=namespaces,
            )
            if lot_result:
                award_id = lot_result[0].xpath(
                    "cbc:ID[@schemeName='result']/text()",
                    namespaces=namespaces,
                )
                if award_id:
                    contract_data["awardID"] = award_id[0]

            result["contracts"].append(contract_data)

    return result if result["contracts"] else None


def merge_contract_url(release_json, contract_url_data):
    if not contract_url_data:
        logger.warning("No contract URL data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_url_data["contracts"]:
        existing_contract = next(
            (c for c in existing_contracts if c["id"] == new_contract["id"]),
            None,
        )
        if existing_contract:
            existing_documents = existing_contract.setdefault("documents", [])
            for new_document in new_contract["documents"]:
                if not any(d["id"] == new_document["id"] for d in existing_documents):
                    existing_documents.append(new_document)
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        f"Merged contract URL data for {len(contract_url_data['contracts'])} contracts",
    )
