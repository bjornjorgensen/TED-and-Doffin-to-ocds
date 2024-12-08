# converters/bt_202_Contract.py

import logging
import uuid

from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_modification_summary(
    xml_content: str | bytes,
) -> dict | None:
    """Parse contract modification summary from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing contract information

    Returns:
        Optional[Dict]: Dictionary containing contract information, or None if no data found
        The structure follows the format:
        {
            "contracts": [
                {
                    "id": str,
                    "amendments": [
                        {
                            "id": str,
                            "description": str
                        }
                    ],
                    "awardID": str  # Optional
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

    modifications = root.xpath(
        "//efac:ContractModification",
        namespaces=namespaces,
    )

    for modification in modifications:
        contract_id = modification.xpath(
            "efac:Change/efac:ChangedSection/efbc:ChangedSectionIdentifier/text()",
            namespaces=namespaces,
        )
        change_desc = modification.xpath(
            "efac:Change/efbc:ChangeDescription/text()",
            namespaces=namespaces,
        )

        if contract_id and change_desc:
            # Find all related lot results
            lot_results = root.xpath(
                f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']='{contract_id[0]}']",
                namespaces=namespaces,
            )

            contract_data = {
                "id": contract_id[0],
                "amendments": [
                    {"id": str(uuid.uuid4()), "description": change_desc[0]}
                ],
            }

            # Handle award IDs based on number of lot results
            award_ids = [
                lot.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)[
                    0
                ]
                for lot in lot_results
                if lot.xpath(
                    "cbc:ID[@schemeName='result']/text()", namespaces=namespaces
                )
            ]

            if len(award_ids) == 1:
                contract_data["awardID"] = award_ids[0]
            elif len(award_ids) > 1:
                contract_data["awardIDs"] = award_ids

            result["contracts"].append(contract_data)

    return result if result["contracts"] else None


def merge_contract_modification_summary(
    release_json: dict, modification_data: dict | None
) -> None:
    """Merge contract modification summary data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        modification_data (Optional[Dict]): The source data containing contracts
            to be merged. If None, function returns without making changes.

    """
    if not modification_data:
        return

    existing_contracts = release_json.setdefault("contracts", [])
    for new_contract in modification_data["contracts"]:
        existing_contract = next(
            (c for c in existing_contracts if c["id"] == new_contract["id"]),
            None,
        )
        if existing_contract:
            for new_amendment in new_contract["amendments"]:
                existing_amendments = existing_contract.setdefault("amendments", [])
                existing_amendment = next(
                    (a for a in existing_amendments if a["id"] == new_amendment["id"]),
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
