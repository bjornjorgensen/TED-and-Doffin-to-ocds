# converters/opt_316_contract.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_contract_technical_identifier(xml_content):
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

    result = {"contracts": []}

    # Parse SettledContract information
    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract", namespaces=namespaces
    )

    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath(
            "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces
        )

        if contract_id:
            contract = {"id": contract_id[0]}
            result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_contract_technical_identifier(
    release_json, contract_technical_identifier_data
):
    if not contract_technical_identifier_data:
        logger.info("No Contract Technical Identifier data to merge.")
        return

    contracts = release_json.setdefault("contracts", [])

    for new_contract in contract_technical_identifier_data["contracts"]:
        if not any(contract["id"] == new_contract["id"] for contract in contracts):
            contracts.append(new_contract)

    logger.info(
        "Merged Contract Technical Identifier data for %d contracts.",
        len(contract_technical_identifier_data["contracts"]),
    )
