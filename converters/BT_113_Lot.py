# converters/BT_113_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_framework_max_participants(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lots": []}}
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        max_participants = lot.xpath("cac:TenderingProcess/cac:FrameworkAgreement/cbc:MaximumOperatorQuantity/text()", namespaces=namespaces)

        if max_participants:
            lot_data = {
                "id": lot_id,
                "techniques": {
                    "frameworkAgreement": {
                        "maximumParticipants": int(max_participants[0])
                    }
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_framework_max_participants(release_json, max_participants_data):
    if not max_participants_data:
        logger.warning("No Framework Maximum Participants data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "lots" not in release_json["tender"]:
        release_json["tender"]["lots"] = []

    existing_lots = release_json["tender"]["lots"]
    new_lots = max_participants_data["tender"]["lots"]

    for new_lot in new_lots:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            if "techniques" not in existing_lot:
                existing_lot["techniques"] = {}
            if "frameworkAgreement" not in existing_lot["techniques"]:
                existing_lot["techniques"]["frameworkAgreement"] = {}
            existing_lot["techniques"]["frameworkAgreement"]["maximumParticipants"] = new_lot["techniques"]["frameworkAgreement"]["maximumParticipants"]
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Framework Maximum Participants data for {len(new_lots)} lots")