# converters/BT_13713_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_result_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult"
    lot_results = root.xpath(xpath, namespaces=namespaces)

    awards = []
    for lot_result in lot_results:
        award_id = lot_result.xpath("cbc:ID", namespaces=namespaces)[0].text
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID", namespaces=namespaces)[
            0
        ].text

        awards.append({"id": award_id, "relatedLots": [lot_id]})

    if awards:
        return {"awards": awards}
    logger.info("No lot result identifiers found")
    return None


def merge_lot_result_identifier(release_json, lot_result_data):
    if not lot_result_data:
        logger.warning("No lot result identifier data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in lot_result_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )

        if existing_award:
            existing_lots = set(existing_award.get("relatedLots", []))
            existing_lots.update(new_award["relatedLots"])
            existing_award["relatedLots"] = list(existing_lots)
            logger.info(f"Updated relatedLots for award {new_award['id']}")
        else:
            existing_awards.append(new_award)
            logger.info(f"Added new award with id: {new_award['id']}")
