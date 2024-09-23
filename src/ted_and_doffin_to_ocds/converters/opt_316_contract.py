# converters/OPT_316_Contract.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_contract_technical_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"contracts": []}
    settled_contracts = root.xpath(
        "//efac:noticeResult/efac:SettledContract",
        namespaces=namespaces,
    )

    for contract in settled_contracts:
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )
        if contract_id:
            result["contracts"].append({"id": contract_id[0]})

    return result if result["contracts"] else None


def merge_contract_technical_identifier(release_json, contract_tech_id_data):
    if not contract_tech_id_data:
        logger.warning("No Contract Technical Identifier data to merge")
        return

    if "contracts" not in release_json:
        release_json["contracts"] = []

    for new_contract in contract_tech_id_data["contracts"]:
        if not any(c["id"] == new_contract["id"] for c in release_json["contracts"]):
            release_json["contracts"].append(new_contract)

    logger.info(
        f"Merged Contract Technical Identifier data for {len(contract_tech_id_data['contracts'])} contracts",
    )
