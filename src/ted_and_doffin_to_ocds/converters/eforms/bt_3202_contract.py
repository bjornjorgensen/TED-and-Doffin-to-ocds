"""Converter for BT-3202-Contract: Contract tender ID and related information.

This module handles mapping of contract tender IDs and relationships between:
- Contracts and their related bids
- Awards and their suppliers
- Supplier organizations and their roles
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_contract_tender_id(xml_content: str | bytes) -> dict | None:
    """Parse contract and tender relationships following BT-3202.

    For each SettledContract:
    1. Gets LotTender ID and adds to contract's relatedBids
    2. Gets associated TenderingParty through LotTender reference
    3. Gets organization IDs from Tenderer elements
    4. Creates supplier parties for each organization
    5. Creates awards linking suppliers to lots from LotResult
    6. Links awards to contracts through SettledContract references

    Args:
        xml_content: XML string or bytes containing the notice

    Returns:
        dict | None: Dictionary containing:
            {
                "parties": [{
                    "id": str,  # Organization ID
                    "roles": ["supplier"]
                }],
                "awards": [{
                    "id": str,  # Award/result ID
                    "suppliers": [{"id": str}],  # Organization references
                    "relatedLots": [str]  # Lot IDs
                }],
                "contracts": [{
                    "id": str,  # Contract ID
                    "relatedBids": [str]  # Tender/bid IDs
                }]
            }
        Returns None if no relevant data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError as e:
        logger.error(f"Failed to parse XML: {e}")
        return None

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"parties": [], "awards": [], "contracts": []}

    notice_results = root.xpath(
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult",
        namespaces=namespaces,
    )

    if not notice_results:
        return None

    for notice_result in notice_results:
        settled_contracts = notice_result.xpath(
            "efac:SettledContract", namespaces=namespaces
        )

        for settled_contract in settled_contracts:
            try:
                contract_id = settled_contract.xpath(
                    "cbc:ID/text()", namespaces=namespaces
                )[0]

                supplier_ids = []
                tenderers = notice_result.xpath(
                    f".//efac:TenderingParty/efac:Tenderer[ancestor::efac:NoticeResult//efac:SettledContract/cbc:ID/text()='{contract_id}']",
                    namespaces=namespaces,
                )

                for tenderer in tenderers:
                    org_id = tenderer.xpath("cbc:ID/text()", namespaces=namespaces)[0]
                    supplier_ids.append(org_id)

                    new_party = {"id": org_id, "roles": ["supplier"]}
                    existing_party = next(
                        (p for p in result["parties"] if p["id"] == org_id), None
                    )
                    if existing_party:
                        if "supplier" not in existing_party["roles"]:
                            existing_party["roles"].append("supplier")
                    else:
                        result["parties"].append(new_party)

                lot_results = notice_result.xpath(
                    f".//efac:LotResult[efac:SettledContract/cbc:ID/text()='{contract_id}']",
                    namespaces=namespaces,
                )

                lot_tender_id = settled_contract.xpath(
                    "efac:LotTender/cbc:ID/text()", namespaces=namespaces
                )[0]
                result["contracts"].append(
                    {"id": contract_id, "relatedBids": [lot_tender_id]}
                )

                for lot_result in lot_results:
                    award_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[
                        0
                    ]
                    lot_id = lot_result.xpath(
                        "efac:TenderLot/cbc:ID/text()", namespaces=namespaces
                    )[0]

                    result["awards"].append(
                        {
                            "id": award_id,
                            "suppliers": [{"id": id} for id in supplier_ids],
                            "relatedLots": [lot_id],
                        }
                    )

            except (IndexError, AttributeError) as e:
                logger.warning(f"Skipping incomplete contract data: {e}")
                continue

    return result if any(result.values()) else None


def merge_contract_tender_id(release_json: dict, contract_tender_id_data: dict) -> None:
    """Merge contract tender ID data into the release JSON.

    Args:
        release_json: Target release JSON object
        contract_tender_id_data: Contract tender ID data to merge

    """
    if not contract_tender_id_data:
        return

    if not isinstance(contract_tender_id_data, dict):
        logger.error("Invalid contract data format")
        return

    # Merge parties
    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for new_party in contract_tender_id_data["parties"]:
        if new_party["id"] in existing_parties:
            existing_parties[new_party["id"]]["roles"] = list(
                set(
                    existing_parties[new_party["id"]].get("roles", [])
                    + new_party["roles"]
                )
            )
        else:
            existing_parties[new_party["id"]] = new_party
    release_json["parties"] = list(existing_parties.values())

    # Merge awards
    existing_awards = {award["id"]: award for award in release_json.get("awards", [])}
    for new_award in contract_tender_id_data["awards"]:
        if new_award["id"] in existing_awards:
            # Update suppliers and lots
            existing_award = existing_awards[new_award["id"]]
            existing_award["suppliers"] = list(
                {
                    s["id"]: s
                    for s in existing_award.get("suppliers", [])
                    + new_award["suppliers"]
                }.values()
            )
            existing_award["relatedLots"] = list(
                set(existing_award.get("relatedLots", []) + new_award["relatedLots"])
            )
        else:
            existing_awards[new_award["id"]] = new_award
    release_json["awards"] = list(existing_awards.values())

    # Merge contracts
    existing_contracts = {
        contract["id"]: contract for contract in release_json.get("contracts", [])
    }
    for new_contract in contract_tender_id_data["contracts"]:
        if new_contract["id"] in existing_contracts:
            # Update related bids
            existing_contracts[new_contract["id"]]["relatedBids"] = list(
                set(
                    existing_contracts[new_contract["id"]].get("relatedBids", [])
                    + new_contract["relatedBids"]
                )
            )
        else:
            existing_contracts[new_contract["id"]] = new_contract
    release_json["contracts"] = list(existing_contracts.values())

    logger.info(
        "Merged Contract Tender ID data for %d contracts",
        len(contract_tender_id_data["contracts"]),
    )
