# converters/BT_124_Tool_Atypical_URL.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tool_atypical_url(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"lots": [], "tender": {}}

    # Process BT-124-Lot
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        atypical_url = lot.xpath("cac:TenderingProcess/cbc:AccessToolsURI/text()", namespaces=namespaces)
        
        if atypical_url:
            result["lots"].append({
                "id": lot_id,
                "communication": {
                    "atypicalToolUrl": atypical_url[0]
                }
            })

    # Process BT-124-Part
    part_url = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cbc:AccessToolsURI/text()", namespaces=namespaces)
    if part_url:
        result["tender"]["communication"] = {
            "atypicalToolUrl": part_url[0]
        }

    return result if (result["lots"] or result["tender"]) else None

def merge_tool_atypical_url(release_json, atypical_url_data):
    if not atypical_url_data:
        logger.warning("No Tool Atypical URL data to merge")
        return

    tender = release_json.setdefault("tender", {})

    # Merge BT-124-Lot
    if atypical_url_data.get("lots"):
        existing_lots = tender.setdefault("lots", [])
        for new_lot in atypical_url_data["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("communication", {})["atypicalToolUrl"] = new_lot["communication"]["atypicalToolUrl"]
            else:
                existing_lots.append(new_lot)
        logger.info(f"Merged Tool Atypical URL data for {len(atypical_url_data['lots'])} lots")

    # Merge BT-124-Part
    if atypical_url_data.get("tender", {}).get("communication"):
        tender.setdefault("communication", {})["atypicalToolUrl"] = atypical_url_data["tender"]["communication"]["atypicalToolUrl"]
        logger.info("Merged Tool Atypical URL data for tender")