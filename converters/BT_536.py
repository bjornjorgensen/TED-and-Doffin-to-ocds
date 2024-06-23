from lxml import etree
from utils.date_conversion import convert_to_iso_format

def parse_duration_start_date(xml_content, scheme_name):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    result = {"tender": {"lots": []}} if scheme_name == 'Lot' else {"tender": {"contractPeriod": {}}}

    # Parse for the specific scheme
    start_date_elements = root.xpath(f"/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='{scheme_name}']/cac:ProcurementProject/cac:PlannedPeriod/cbc:StartDate", namespaces=namespaces)
    
    for element in start_date_elements:
        start_date = convert_to_iso_format(element.text, is_start_date=True)
        if scheme_name == 'Lot':
            lot_id = element.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID/text()", namespaces=namespaces)[0]
            lot = next((lot for lot in result["tender"]["lots"] if lot["id"] == lot_id), None)
            if not lot:
                lot = {"id": lot_id, "contractPeriod": {}}
                result["tender"]["lots"].append(lot)
            lot["contractPeriod"]["startDate"] = start_date
        else:
            result["tender"]["contractPeriod"]["startDate"] = start_date

    return result if (scheme_name == 'Lot' and result["tender"]["lots"]) or (scheme_name == 'Part' and result["tender"]["contractPeriod"].get("startDate")) else None

def merge_duration_start_date(release_json, duration_start_date_data, scheme_name):
    if duration_start_date_data and "tender" in duration_start_date_data:
        tender = release_json.setdefault("tender", {})
        
        if scheme_name == 'Lot':
            existing_lots = tender.setdefault("lots", [])
            for new_lot in duration_start_date_data["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot["contractPeriod"] = new_lot["contractPeriod"]
                else:
                    existing_lots.append(new_lot)
        else:
            tender["contractPeriod"] = duration_start_date_data["tender"]["contractPeriod"]
