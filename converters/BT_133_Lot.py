# converters/BT_133_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_public_opening_place(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        opening_place = lot.xpath(".//cac:TenderingProcess/cac:OpenTenderEvent/cac:OccurenceLocation/cbc:Description/text()", namespaces=namespaces)

        if opening_place:
            lot_data = {
                "id": lot_id,
                "bidOpening": {
                    "location": {
                        "description": opening_place[0]
                    }
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_public_opening_place(release_json, public_opening_place_data):
    if not public_opening_place_data:
        logger.warning("No Public Opening Place data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in public_opening_place_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("bidOpening", {}).setdefault("location", {}).update(new_lot["bidOpening"]["location"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Public Opening Place data for {len(public_opening_place_data['tender']['lots'])} lots")