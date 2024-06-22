# converters/BT_36.py
from lxml import etree

def parse_duration_period(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"lots": []}}

    def calculate_duration_in_days(duration, unit_code):
        duration = float(duration)
        if unit_code == "DAY":
            return int(duration)
        elif unit_code == "MONTH":
            return int(duration * 30)
        elif unit_code == "YEAR":
            return int(duration * 365)
        else:
            # For specific days of the week or month, we'd need more information to convert accurately
            # For now, we'll just return the original duration
            return int(duration)

    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        duration_element = lot_element.xpath("cac:ProcurementProject/cac:PlannedPeriod/cbc:DurationMeasure", namespaces=namespaces)
        
        if duration_element:
            duration = duration_element[0].text
            unit_code = duration_element[0].get("unitCode")
            duration_in_days = calculate_duration_in_days(duration, unit_code)
            
            lot = {
                "id": lot_id,
                "contractPeriod": {
                    "durationInDays": duration_in_days
                }
            }
            result["tender"]["lots"].append(lot)
    
    # Parse Part
    part_element = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:DurationMeasure", namespaces=namespaces)
    if part_element:
        duration = part_element[0].text
        unit_code = part_element[0].get("unitCode")
        duration_in_days = calculate_duration_in_days(duration, unit_code)
        
        result["tender"]["contractPeriod"] = {
            "durationInDays": duration_in_days
        }
    
    return result if (result["tender"]["lots"] or "contractPeriod" in result["tender"]) else None

def merge_duration_period(release_json, duration_period_data):
    if duration_period_data and "tender" in duration_period_data:
        tender = release_json.setdefault("tender", {})
        
        # Merge lots
        if "lots" in duration_period_data["tender"]:
            existing_lots = tender.setdefault("lots", [])
            for new_lot in duration_period_data["tender"]["lots"]:
                existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
                if existing_lot:
                    existing_lot["contractPeriod"] = new_lot["contractPeriod"]
                else:
                    existing_lots.append(new_lot)
        
        # Merge tender contractPeriod (Part)
        if "contractPeriod" in duration_period_data["tender"]:
            tender["contractPeriod"] = duration_period_data["tender"]["contractPeriod"]
