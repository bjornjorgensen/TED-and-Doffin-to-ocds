# converters/bt_722_Contract.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_eu_funds(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, str]]] | None:
    """
    Parse the XML content to extract contract EU funds programme information.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed contract EU funds data.
        None: If no relevant data is found.
    """
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
        "//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:SettledContract",
        namespaces=namespaces,
    )

    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath(
            "cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )
        funding_programs = settled_contract.xpath(
            "efac:Funding/cbc:FundingProgramCode[@listName='eu-programme']/text()",
            namespaces=namespaces,
        )

        if contract_id and funding_programs:
            contract = {
                "id": contract_id[0],
                "finance": [{"title": program} for program in funding_programs],
            }

            # Find corresponding LotResult
            lot_result = root.xpath(
                f"//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id[0]}']",
                namespaces=namespaces,
            )
            if lot_result:
                result_id = lot_result[0].xpath(
                    "cbc:ID[@schemeName='result']/text()",
                    namespaces=namespaces,
                )
                if result_id:
                    contract["awardID"] = result_id[0]

            result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_contract_eu_funds(
    release_json: dict, contract_eu_funds_data: dict[str, list[dict[str, str]]] | None
) -> None:
    """
    Merge the parsed contract EU funds data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        contract_eu_funds_data (dict): The parsed contract EU funds data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not contract_eu_funds_data:
        logger.warning("No contract EU funds data to merge")
        return

    if "contracts" not in release_json:
        release_json["contracts"] = []

    for new_contract in contract_eu_funds_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in release_json["contracts"]
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            if "finance" not in existing_contract:
                existing_contract["finance"] = []
            existing_contract["finance"].extend(new_contract["finance"])
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            release_json["contracts"].append(new_contract)

    logger.info(
        "Merged contract EU funds data for %d contracts",
        len(contract_eu_funds_data["contracts"]),
    )
