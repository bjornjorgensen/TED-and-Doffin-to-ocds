# converters/BT_13713.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_result_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    awards = []
    lot_results = root.xpath("//efac:LotResult", namespaces=namespaces)

    for lot_result in lot_results:
        award_id_elements = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)
        if not award_id_elements:
            logger.warning("Award ID not found for a LotResult")
            continue
        award_id = award_id_elements[0]

        lot_id_elements = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        if not lot_id_elements:
            logger.warning(f"Lot ID not found for award {award_id}")
            continue
        lot_id = lot_id_elements[0]

        awards.append({
            "id": award_id,
            "relatedLots": [lot_id]
        })

    return {"awards": awards} if awards else None

def merge_result_lot_identifier(release_json, result_lot_identifier):
    if not result_lot_identifier:
        logger.warning("No Result Lot Identifier data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])
    for new_award in result_lot_identifier["awards"]:
        existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_award.setdefault("relatedLots", []).extend(
                lot for lot in new_award["relatedLots"] if lot not in existing_award.get("relatedLots", [])
            )
        else:
            existing_awards.append(new_award)

    logger.info(f"Merged Result Lot Identifier for {len(result_lot_identifier['awards'])} awards")