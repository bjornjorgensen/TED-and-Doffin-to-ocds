import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_main_contractor(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse main contractor references and their subcontracting relationships.

    For each subcontractor:
    - Gets main contractor organization ID and adds tenderer role
    - Links subcontractors to main contractors in bids
    - Creates subcontracting details in bid structure

    Args:
        xml_content: XML content containing contractor data

    Returns:
        Optional[Dict]: Dictionary containing parties and bids, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["tenderer"]
                }
            ],
            "bids": {
                "details": [
                    {
                        "id": "bid_id",
                        "subcontracting": {
                            "subcontracts": [
                                {
                                    "id": "1",
                                    "subcontractor": {"id": "sub_id"},
                                    "mainContractors": [{"id": "org_id"}]
                                }
                            ]
                        }
                    }
                ]
            }
        }

    """
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

    result = {"parties": [], "bids": {"details": []}}

    # Parse main contractor information
    xpath = "//efac:NoticeResult/efac:TenderingParty/efac:SubContractor"
    subcontractors = root.xpath(xpath, namespaces=namespaces)

    for subcontractor in subcontractors:
        subcontractor_id = subcontractor.xpath(
            "cbc:ID[@schemeName='organization']/text()", namespaces=namespaces
        )
        main_contractor_id = subcontractor.xpath(
            "efac:MainContractor/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )

        if subcontractor_id and main_contractor_id:
            # Add main contractor to parties
            result["parties"].append(
                {"id": main_contractor_id[0], "roles": ["tenderer"]}
            )

            # Find corresponding LotTender
            lot_tender_id = root.xpath(
                "//efac:NoticeResult/efac:LotTender/cbc:ID[@schemeName='tender']/text()",
                namespaces=namespaces,
            )
            if lot_tender_id:
                bid = next(
                    (
                        bid
                        for bid in result["bids"]["details"]
                        if bid.get("id") == lot_tender_id[0]
                    ),
                    None,
                )
                if not bid:
                    bid = {
                        "id": lot_tender_id[0],
                        "subcontracting": {"subcontracts": []},
                    }
                    result["bids"]["details"].append(bid)

                subcontract = {
                    "id": str(len(bid["subcontracting"]["subcontracts"]) + 1),
                    "subcontractor": {"id": subcontractor_id[0]},
                    "mainContractors": [{"id": main_contractor_id[0]}],
                }
                bid["subcontracting"]["subcontracts"].append(subcontract)

    return result if (result["parties"] or result["bids"]["details"]) else None


def merge_main_contractor(
    release_json: dict[str, Any], main_contractor_data: dict[str, Any] | None
) -> None:
    """Merge main contractor data into the release JSON.

    Args:
        release_json: Target release JSON to update
        main_contractor_data: Contractor data containing organizations and subcontracting

    Effects:
        - Updates parties with tenderer roles
        - Updates bids with subcontracting information
        - Links main contractors to their subcontractors

    """
    if not main_contractor_data:
        logger.info("No Main Contractor data to merge.")
        return

    # Merge parties
    parties = release_json.setdefault("parties", [])
    for new_party in main_contractor_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "tenderer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("tenderer")
        else:
            parties.append(new_party)

    # Merge bids
    bids = release_json.setdefault("bids", {}).setdefault("details", [])
    for new_bid in main_contractor_data["bids"]["details"]:
        existing_bid = next((bid for bid in bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_subcontracts = existing_bid.setdefault(
                "subcontracting", {}
            ).setdefault("subcontracts", [])
            for new_subcontract in new_bid["subcontracting"]["subcontracts"]:
                existing_subcontract = next(
                    (
                        sc
                        for sc in existing_subcontracts
                        if sc["subcontractor"]["id"]
                        == new_subcontract["subcontractor"]["id"]
                    ),
                    None,
                )
                if existing_subcontract:
                    existing_subcontract.setdefault("mainContractors", []).extend(
                        new_subcontract["mainContractors"]
                    )
                else:
                    existing_subcontracts.append(new_subcontract)
        else:
            bids.append(new_bid)

    logger.info(
        "Merged Main Contractor data for %d parties and %d bids.",
        len(main_contractor_data["parties"]),
        len(main_contractor_data["bids"]["details"]),
    )
