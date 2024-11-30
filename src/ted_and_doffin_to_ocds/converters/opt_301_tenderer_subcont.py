# converters/opt_301_tenderer_subcont.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontractor(xml_content):
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

    # Parse subcontractor information
    xpath = "//efac:NoticeResult/efac:TenderingParty/efac:SubContractor"
    subcontractors = root.xpath(xpath, namespaces=namespaces)

    for subcontractor in subcontractors:
        subcontractor_id = subcontractor.xpath(
            "cbc:ID[@schemeName='organization']/text()", namespaces=namespaces
        )

        if subcontractor_id:
            # Add subcontractor to parties
            result["parties"].append(
                {"id": subcontractor_id[0], "roles": ["subcontractor"]}
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
                }
                bid["subcontracting"]["subcontracts"].append(subcontract)

    return result if (result["parties"] or result["bids"]["details"]) else None


def merge_subcontractor(release_json, subcontractor_data) -> None:
    if not subcontractor_data:
        logger.info("No Subcontractor data to merge.")
        return

    # Merge parties
    parties = release_json.setdefault("parties", [])
    for new_party in subcontractor_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "subcontractor" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("subcontractor")
        else:
            parties.append(new_party)

    # Merge bids
    bids = release_json.setdefault("bids", {}).setdefault("details", [])
    for new_bid in subcontractor_data["bids"]["details"]:
        existing_bid = next((bid for bid in bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_subcontracts = existing_bid.setdefault(
                "subcontracting", {}
            ).setdefault("subcontracts", [])
            for new_subcontract in new_bid["subcontracting"]["subcontracts"]:
                if not any(
                    sc["subcontractor"]["id"] == new_subcontract["subcontractor"]["id"]
                    for sc in existing_subcontracts
                ):
                    new_subcontract["id"] = str(len(existing_subcontracts) + 1)
                    existing_subcontracts.append(new_subcontract)
        else:
            bids.append(new_bid)

    logger.info(
        "Merged Subcontractor data for %d parties and %d bids.",
        len(subcontractor_data["parties"]),
        len(subcontractor_data["bids"]["details"]),
    )
