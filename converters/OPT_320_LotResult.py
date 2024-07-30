# converters/OPT_320_LotResult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_identifier_reference(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"awards": []}
    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)

    for lot_result in lot_results:
        award_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        tender_ids = lot_result.xpath("efac:LotTender/cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)

        if award_id and tender_ids:
            award = {
                "id": award_id[0],
                "relatedBids": tender_ids
            }
            result["awards"].append(award)

    return result if result["awards"] else None

def merge_tender_identifier_reference(release_json, tender_id_data):
    if not tender_id_data:
        logger.warning("No Tender Identifier Reference data to merge")
        return

    if "awards" not in release_json:
        release_json["awards"] = []

    for new_award in tender_id_data["awards"]:
        existing_award = next((a for a in release_json["awards"] if a["id"] == new_award["id"]), None)
        if existing_award:
            if "relatedBids" not in existing_award:
                existing_award["relatedBids"] = []
            existing_award["relatedBids"].extend(new_award["relatedBids"])
            # Remove duplicates while preserving order
            existing_award["relatedBids"] = list(dict.fromkeys(existing_award["relatedBids"]))
        else:
            release_json["awards"].append(new_award)

    logger.info(f"Merged Tender Identifier Reference data for {len(tender_id_data['awards'])} awards")