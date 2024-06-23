# converters/BT_632_Tool_Name.py
from lxml import etree

def parse_tool_name(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {
        "lots": {},
        "part": None
    }

    # Parse BT-632-Lot
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        tool_name = lot.xpath(".//efext:EformsExtension/efbc:AccessToolName/text()", namespaces=namespaces)
        if tool_name:
            result["lots"][lot_id] = tool_name[0]

    # Parse BT-632-Part
    part_tool_name = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']//efext:EformsExtension/efbc:AccessToolName/text()", namespaces=namespaces)
    if part_tool_name:
        result["part"] = part_tool_name[0]

    return result

def merge_tool_name(release_json, tool_name_data):
    tender = release_json.setdefault("tender", {})

    # Merge BT-632-Lot
    lots = tender.setdefault("lots", [])
    for lot_id, tool_name in tool_name_data["lots"].items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        communication = lot.setdefault("communication", {})
        communication["atypicalToolName"] = tool_name

    # Merge BT-632-Part
    if tool_name_data["part"]:
        communication = tender.setdefault("communication", {})
        communication["atypicalToolName"] = tool_name_data["part"]

    return release_json