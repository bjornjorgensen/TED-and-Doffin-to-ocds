# converters/opt_320_lotresult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_identifier_reference(xml_content):
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

    result = {"awards": []}

    # Parse LotResult information
    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult", namespaces=namespaces
    )

    for lot_result in lot_results:
        lot_tenders = lot_result.xpath(
            "efac:LotTender/cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )

        if lot_tenders:
            award = {"relatedBids": lot_tenders}
            result["awards"].append(award)

    return result if result["awards"] else None


def merge_tender_identifier_reference(release_json, tender_identifier_data) -> None:
    if not tender_identifier_data:
        logger.info("No Tender Identifier Reference data to merge.")
        return

    awards = release_json.setdefault("awards", [])

    if not awards:
        awards.extend(tender_identifier_data["awards"])
    else:
        for new_award in tender_identifier_data["awards"]:
            if awards[-1].get("relatedBids"):
                awards[-1]["relatedBids"].extend(new_award["relatedBids"])
            else:
                awards[-1]["relatedBids"] = new_award["relatedBids"]

    logger.info(
        "Merged Tender Identifier Reference data for %d awards.",
        len(tender_identifier_data["awards"]),
    )
