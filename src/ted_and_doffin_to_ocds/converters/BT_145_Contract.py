# converters/BT_145_Contract.py

import logging
from lxml import etree
from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_contract_conclusion_date(xml_content):
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

    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract", namespaces=namespaces,
    )

    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath(
            "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces,
        )
        issue_date = settled_contract.xpath(
            "cbc:IssueDate/text()", namespaces=namespaces,
        )

        if contract_id and issue_date:
            contract = {"id": contract_id[0], "dateSigned": end_date(issue_date[0])}
            result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_contract_conclusion_date(release_json, contract_conclusion_date_data):
    if not contract_conclusion_date_data:
        logger.warning("No Contract Conclusion Date data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_conclusion_date_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_contract["dateSigned"] = new_contract["dateSigned"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        f"Merged Contract Conclusion Date data for {len(contract_conclusion_date_data['contracts'])} contracts",
    )
