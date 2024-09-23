# converters/OPT_315_LotResult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_contract_identifier_reference(xml_content):
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
    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces,
    )

    for lot_result in lot_results:
        award_ids = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()", namespaces=namespaces,
        )
        contract_ids = lot_result.xpath(
            "efac:SettledContract/cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )

        if contract_ids:
            for contract_id in contract_ids:
                contract = {
                    "id": contract_id,
                }
                if award_ids:
                    contract["awardID"] = award_ids[0]
                result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_contract_identifier_reference(release_json, contract_id_data):
    if not contract_id_data:
        logger.warning("No Contract Identifier Reference data to merge")
        return

    if "contracts" not in release_json:
        release_json["contracts"] = []

    for new_contract in contract_id_data["contracts"]:
        existing_contract = next(
            (c for c in release_json["contracts"] if c["id"] == new_contract["id"]),
            None,
        )
        if existing_contract:
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            release_json["contracts"].append(new_contract)

    logger.info(
        f"Merged Contract Identifier Reference data for {len(contract_id_data['contracts'])} contracts",
    )
