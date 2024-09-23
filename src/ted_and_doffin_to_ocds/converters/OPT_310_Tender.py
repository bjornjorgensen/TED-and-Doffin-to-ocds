# converters/OPT_310_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_tendering_party_id_reference(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": [], "bids": {"details": []}}
    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        if not tender_id:
            logger.warning("Tender ID not found for a LotTender")
            continue

        tender_id = tender_id[0]
        tendering_party_id = lot_tender.xpath(
            "efac:TenderingParty/cbc:ID/text()",
            namespaces=namespaces,
        )

        if tendering_party_id:
            tendering_party_id = tendering_party_id[0]
            tendering_party = root.xpath(
                f"//efac:NoticeResult/efac:TenderingParty[cbc:ID/text()='{tendering_party_id}']",
                namespaces=namespaces,
            )

            if tendering_party:
                bid = {"id": tender_id, "tenderers": []}
                tenderers = tendering_party[0].xpath(
                    "efac:Tenderer/cbc:ID[@schemeName='organization']/text()",
                    namespaces=namespaces,
                )

                for tenderer_id in tenderers:
                    bid["tenderers"].append({"id": tenderer_id})

                    # Add or update party
                    party = next(
                        (p for p in result["parties"] if p["id"] == tenderer_id),
                        None,
                    )
                    if party:
                        if "tenderer" not in party["roles"]:
                            party["roles"].append("tenderer")
                    else:
                        result["parties"].append(
                            {"id": tenderer_id, "roles": ["tenderer"]},
                        )

                result["bids"]["details"].append(bid)

    logger.info(f"Parsed Tendering Party ID Reference data: {result}")
    return result if (result["parties"] or result["bids"]["details"]) else None


def merge_tendering_party_id_reference(release_json, tendering_party_data):
    if not tendering_party_data:
        logger.warning("No Tendering Party ID Reference data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    for new_party in tendering_party_data["parties"]:
        existing_party = next(
            (p for p in existing_parties if p["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["roles"] = list(
                set(existing_party.get("roles", []) + new_party["roles"]),
            )
        else:
            existing_parties.append(new_party)

    existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
    for new_bid in tendering_party_data["bids"]["details"]:
        existing_bid = next(
            (b for b in existing_bids if b["id"] == new_bid["id"]),
            None,
        )
        if existing_bid:
            existing_tenderers = existing_bid.setdefault("tenderers", [])
            for new_tenderer in new_bid["tenderers"]:
                if new_tenderer not in existing_tenderers:
                    existing_tenderers.append(new_tenderer)
        else:
            existing_bids.append(new_bid)

    logger.info(f"Merged Tendering Party ID Reference data: {release_json}")
