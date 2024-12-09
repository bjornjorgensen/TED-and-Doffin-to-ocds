# converters/bt_145_Contract.py

import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_contract_conclusion_date(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """Parses the contract conclusion date from XML content in both old and new formats.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, List[Dict[str, Any]]]]: A dictionary containing contract conclusion dates, or None if no contracts are found.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logging.exception("Failed to parse XML content")
        return None

    # Map of contract IDs to award IDs
    contract_awards = {}

    # First find all lot results to map contracts to awards
    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=NAMESPACES,
    )

    for lot_result in lot_results:
        award_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=NAMESPACES,
        )
        contract_id = lot_result.xpath(
            ".//efac:SettledContract/cbc:ID[@schemeName='contract']/text()",
            namespaces=NAMESPACES,
        )
        if award_id and contract_id:
            contract_awards[contract_id[0]] = award_id[0]

    # Then process settled contracts
    result = {"contracts": []}

    # Try different XPath patterns for settled contracts
    settled_contracts = root.xpath(
        """
        //efac:NoticeResult/efac:SettledContract |
        //efac:noticeResult/efac:SettledContract |
        //ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/
        efext:EformsExtension/efac:NoticeResult/efac:SettledContract
        """,
        namespaces=NAMESPACES,
    )

    for settled_contract in settled_contracts:
        contract_id = settled_contract.xpath(
            "cbc:ID[@schemeName='contract']/text()",
            namespaces=NAMESPACES,
        )
        issue_date = settled_contract.xpath(
            "cbc:IssueDate/text()",
            namespaces=NAMESPACES,
        )

        if contract_id and issue_date:
            contract = {"id": contract_id[0], "dateSigned": end_date(issue_date[0])}

            # Add award ID if we found a mapping
            if contract_id[0] in contract_awards:
                contract["awardID"] = contract_awards[contract_id[0]]

            result["contracts"].append(contract)
            logger.info("Found contract %s with date %s", contract_id[0], issue_date[0])

    return result if result["contracts"] else None


def merge_contract_conclusion_date(
    release_json: dict[str, Any],
    contract_conclusion_date_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """Merges the contract conclusion date data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        contract_conclusion_date_data (Optional[Dict[str, List[Dict[str, Any]]]]): The contract conclusion date data to merge.

    Returns:
        None

    """
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
        "Merged Contract Conclusion Date data for %d contracts",
        len(contract_conclusion_date_data["contracts"]),
    )
