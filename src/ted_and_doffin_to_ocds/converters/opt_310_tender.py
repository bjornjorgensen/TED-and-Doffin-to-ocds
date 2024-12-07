# converters/opt_310_tender.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tendering_party_id_reference(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse tendering party references and link tenderers to bids.

    For each lot tender:
    - Gets corresponding tendering party by ID
    - Links tenderer organizations to bids
    - Adds tenderer role to organizations

    Args:
        xml_content: XML content containing tender data

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
                        "tenderers": [
                            {
                                "id": "org_id"
                            }
                        ]
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

    # Parse LotTender information
    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender", namespaces=namespaces
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )
        tendering_party_id = lot_tender.xpath(
            "efac:TenderingParty/cbc:ID[@schemeName='tendering-party']/text()",
            namespaces=namespaces,
        )

        if tender_id and tendering_party_id:
            # Find corresponding TenderingParty
            tendering_party = root.xpath(
                f"//efac:NoticeResult/efac:TenderingParty[cbc:ID[@schemeName='tendering-party']/text()='{tendering_party_id[0]}']",
                namespaces=namespaces,
            )

            if tendering_party:
                bid = {"id": tender_id[0], "tenderers": []}

                # Process Tenderers
                tenderers = tendering_party[0].xpath(
                    "efac:Tenderer", namespaces=namespaces
                )
                for tenderer in tenderers:
                    org_id = tenderer.xpath(
                        "cbc:ID[@schemeName='organization']/text()",
                        namespaces=namespaces,
                    )
                    if org_id:
                        # Add organization to parties
                        if not any(
                            party["id"] == org_id[0] for party in result["parties"]
                        ):
                            result["parties"].append(
                                {"id": org_id[0], "roles": ["tenderer"]}
                            )

                        # Add tenderer to bid
                        bid["tenderers"].append({"id": org_id[0]})

                result["bids"]["details"].append(bid)

    return result if (result["parties"] or result["bids"]["details"]) else None


def merge_tendering_party_id_reference(
    release_json: dict[str, Any], tendering_party_data: dict[str, Any] | None
) -> None:
    """
    Merge tendering party data into the release JSON.

    Args:
        release_json: Target release JSON to update
        tendering_party_data: Tendering party data containing organizations and bids

    Effects:
        - Updates parties with tenderer roles
        - Updates bids with tenderer references
        - Maintains relationships between tenderers and bids
    """
    if not tendering_party_data:
        logger.info("No Tendering Party ID Reference data to merge.")
        return

    # Merge parties
    parties = release_json.setdefault("parties", [])
    for new_party in tendering_party_data["parties"]:
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
    for new_bid in tendering_party_data["bids"]["details"]:
        existing_bid = next((bid for bid in bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_tenderers = existing_bid.setdefault("tenderers", [])
            for new_tenderer in new_bid["tenderers"]:
                if not any(t["id"] == new_tenderer["id"] for t in existing_tenderers):
                    existing_tenderers.append(new_tenderer)
        else:
            bids.append(new_bid)

    logger.info(
        "Merged Tendering Party ID Reference data for %d parties and %d bids.",
        len(tendering_party_data["parties"]),
        len(tendering_party_data["bids"]["details"]),
    )
