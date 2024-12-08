import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_identifier(xml_content: str | bytes) -> dict | None:
    """Parse contract identifiers from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing contract information

    Returns:
        Optional[Dict]: Dictionary containing contract information, or None if no data found
        The structure follows the format:
        {
            "contracts": [
                {
                    "id": str,
                    "identifiers": [
                        {
                            "id": str,
                            "scheme": str
                        }
                    ],
                    "awardID": str  # Optional, included if award mapping exists
                }
            ]
        }

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
        "//efac:NoticeResult/efac:SettledContract",
        namespaces=namespaces,
    )

    # First map contracts to awards
    contract_awards = {}
    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )
    for lot_result in lot_results:
        award_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        contract_id = lot_result.xpath(
            "efac:SettledContract/cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )
        if award_id and contract_id:
            contract_awards[contract_id[0]] = award_id[0]

    # Process each contract
    for contract in settled_contracts:
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()",
            namespaces=namespaces,
        )
        reference_id = contract.xpath(
            "efac:ContractReference/cbc:ID/text()",
            namespaces=namespaces,
        )

        if contract_id and reference_id:
            contract_data = {
                "id": contract_id[0],
                "identifiers": [
                    {
                        "id": reference_id[0],
                        "scheme": "NL-TENDERNED",  # Could be made configurable
                    }
                ],
            }

            # Add award ID if mapping exists
            if contract_id[0] in contract_awards:
                contract_data["awardID"] = contract_awards[contract_id[0]]

            result["contracts"].append(contract_data)

    return result if result["contracts"] else None


def merge_contract_identifier(
    release_json: dict, contract_identifier_data: dict | None
) -> None:
    """Merge contract identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        contract_identifier_data (Optional[Dict]): The source data containing contracts
            to be merged. If None, function returns without making changes.

    """
    if not contract_identifier_data:
        return

    existing_contracts = release_json.setdefault("contracts", [])
    for new_contract in contract_identifier_data["contracts"]:
        existing_contract = next(
            (c for c in existing_contracts if c["id"] == new_contract["id"]),
            None,
        )
        if existing_contract:
            existing_contract.setdefault("identifiers", []).extend(
                new_contract["identifiers"]
            )
            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Contract Identifier data for %d contracts",
        len(contract_identifier_data["contracts"]),
    )
    logger.debug(
        "Release JSON after merging Contract Identifier data: %s", release_json
    )
