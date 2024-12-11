"""Converter for OPT-310-Tender: Tendering Party ID Reference mapping."""

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tendering_party_id_reference(xml_content: str | bytes) -> dict | None:
    """Parse tendering party references and link tenderers to bids.

    Args:
        xml_content: XML content containing tender data

    Returns:
        dict | None: Dictionary containing parties and bids data, or None if no data found

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
    }

    result = {"parties": [], "bids": {"details": []}}

    # Find all LotTender elements
    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender", namespaces=namespaces
    )

    for lot_tender in lot_tenders:
        try:
            # Get tender ID
            tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)[0]

            # Get tendering party reference ID
            tendering_party_id = lot_tender.xpath(
                "efac:TenderingParty/cbc:ID/text()", namespaces=namespaces
            )[0]

            # Find matching TenderingParty
            tendering_party = root.xpath(
                f"//efac:NoticeResult/efac:TenderingParty[cbc:ID/text()='{tendering_party_id}']",
                namespaces=namespaces,
            )[0]

            # Create bid object
            bid = {"id": tender_id, "tenderers": []}

            # Process all Tenderer elements
            tenderers = tendering_party.xpath("efac:Tenderer", namespaces=namespaces)
            for tenderer in tenderers:
                org_id = tenderer.xpath("cbc:ID/text()", namespaces=namespaces)[0]

                # Add organization to parties if new
                if not any(p["id"] == org_id for p in result["parties"]):
                    result["parties"].append({"id": org_id, "roles": ["tenderer"]})

                # Add tenderer reference to bid
                bid["tenderers"].append({"id": org_id})

            result["bids"]["details"].append(bid)

        except (IndexError, AttributeError) as e:
            logger.warning(f"Skipping incomplete tender data: {e}")
            continue

    return result if result["bids"]["details"] else None


def merge_tendering_party_id_reference(
    release_json: dict, tendering_data: dict | None
) -> None:
    """Merge tendering party data into release JSON.

    Args:
        release_json: Target release JSON object
        tendering_data: Tendering party data to merge

    """
    if not tendering_data:
        return

    # Merge parties with tenderer roles
    existing_parties = {p["id"]: p for p in release_json.get("parties", [])}
    for new_party in tendering_data["parties"]:
        if new_party["id"] in existing_parties:
            roles = existing_parties[new_party["id"]].setdefault("roles", [])
            if "tenderer" not in roles:
                roles.append("tenderer")
        else:
            existing_parties[new_party["id"]] = new_party
    release_json["parties"] = list(existing_parties.values())

    # Merge bids
    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    bid_map = {b["id"]: b for b in existing_bids}

    for new_bid in tendering_data["bids"]["details"]:
        if new_bid["id"] in bid_map:
            # Update existing bid tenderers
            existing_tenderers = bid_map[new_bid["id"]].setdefault("tenderers", [])
            for tenderer in new_bid["tenderers"]:
                if not any(t["id"] == tenderer["id"] for t in existing_tenderers):
                    existing_tenderers.append(tenderer)
        else:
            existing_bids.append(new_bid)

    logger.info(
        "Merged tendering party data: %d parties, %d bids",
        len(tendering_data["parties"]),
        len(tendering_data["bids"]["details"]),
    )
