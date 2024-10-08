# converters/opt_310_tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_tendering_party_id_reference(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    }

    result = {"parties": [], "bids": {"details": []}}

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
        related_lots = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces
        )

        if tender_id and tendering_party_id:
            tender_id = tender_id[0]
            tendering_party_id = tendering_party_id[0]

            tendering_party = root.xpath(
                f"//efac:NoticeResult/efac:TenderingParty[cbc:ID[@schemeName='tendering-party']/text()='{tendering_party_id}']",
                namespaces=namespaces,
            )

            if tendering_party:
                tenderers = tendering_party[0].xpath(
                    "efac:Tenderer/cbc:ID[@schemeName='organization']/text()",
                    namespaces=namespaces,
                )

                bid = {"id": tender_id, "tenderers": [], "relatedLots": related_lots}
                for tenderer_id in tenderers:
                    result["parties"].append({"id": tenderer_id, "roles": ["tenderer"]})
                    bid["tenderers"].append({"id": tenderer_id})

                result["bids"]["details"].append(bid)

    return result if result["parties"] or result["bids"]["details"] else None


def merge_tendering_party_id_reference(release_json, tendering_party_data):
    if not tendering_party_data:
        logger.info("No Tendering Party ID Reference data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for new_party in tendering_party_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_party.setdefault("roles", []).extend(
                role
                for role in new_party["roles"]
                if role not in existing_party["roles"]
            )
        else:
            parties.append(new_party)

    bids = release_json.setdefault("bids", {}).setdefault("details", [])
    for new_bid in tendering_party_data["bids"]["details"]:
        existing_bid = next((bid for bid in bids if bid["id"] == new_bid["id"]), None)
        if existing_bid:
            existing_tenderers = existing_bid.setdefault("tenderers", [])
            for new_tenderer in new_bid["tenderers"]:
                if new_tenderer not in existing_tenderers:
                    existing_tenderers.append(new_tenderer)
        else:
            bids.append(new_bid)

    logger.info(
        "Merged Tendering Party ID Reference data for %d bids",
        len(tendering_party_data["bids"]["details"]),
    )
