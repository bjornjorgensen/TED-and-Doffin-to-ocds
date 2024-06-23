# converters/BT_5141.py
from lxml import etree

# ISO 3166-1 alpha-3 to alpha-2 conversion dictionary
ISO_3166_CONVERSION = {
    "ALB": "AL", "AND": "AD", "AUT": "AT", "BLR": "BY", "BEL": "BE",
    "BIH": "BA", "BGR": "BG", "HRV": "HR", "CYP": "CY", "CZE": "CZ",
    "DNK": "DK", "EST": "EE", "FIN": "FI", "FRA": "FR", "DEU": "DE",
    "GRC": "GR", "HUN": "HU", "ISL": "IS", "IRL": "IE", "ITA": "IT",
    "KAZ": "KZ", "XKX": "XK", "LVA": "LV", "LIE": "LI", "LTU": "LT",
    "LUX": "LU", "MLT": "MT", "MDA": "MD", "MCO": "MC", "MNE": "ME",
    "NLD": "NL", "MKD": "MK", "NOR": "NO", "POL": "PL", "PRT": "PT",
    "ROU": "RO", "RUS": "RU", "SMR": "SM", "SRB": "RS", "SVK": "SK",
    "SVN": "SI", "ESP": "ES", "SWE": "SE", "CHE": "CH", "TUR": "TR",
    "UKR": "UA", "GBR": "GB", "VAT": "VA"
}

def convert_country_code(alpha3_code):
    return ISO_3166_CONVERSION.get(alpha3_code, alpha3_code)

def parse_place_performance_country_code(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"items": [], "deliveryAddresses": []}}

    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        realized_locations = lot_element.xpath("cac:ProcurementProject/cac:RealizedLocation/cac:Address", namespaces=namespaces)
        
        if realized_locations:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "relatedLot": lot_id,
                "deliveryAddresses": []
            }
            for location in realized_locations:
                country_code = location.xpath("cac:Country/cbc:IdentificationCode/text()", namespaces=namespaces)
                if country_code:
                    item["deliveryAddresses"].append({"country": convert_country_code(country_code[0])})
            if item["deliveryAddresses"]:
                result["tender"]["items"].append(item)

    # Parse Part
    part_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:RealizedLocation/cac:Address", namespaces=namespaces)
    for part_element in part_elements:
        country_code = part_element.xpath("cac:Country/cbc:IdentificationCode/text()", namespaces=namespaces)
        if country_code:
            result["tender"]["deliveryAddresses"].append({"country": convert_country_code(country_code[0])})

    # Parse Procedure
    procedure_elements = root.xpath("/*/cac:ProcurementProject/cac:RealizedLocation/cac:Address", namespaces=namespaces)
    for procedure_element in procedure_elements:
        country_code = procedure_element.xpath("cac:Country/cbc:IdentificationCode/text()", namespaces=namespaces)
        if country_code:
            result["tender"]["deliveryAddresses"].append({"country": convert_country_code(country_code[0])})

    return result if (result["tender"]["items"] or result["tender"]["deliveryAddresses"]) else None

def merge_place_performance_country_code(release_json, place_performance_country_code_data):
    if place_performance_country_code_data and "tender" in place_performance_country_code_data:
        tender = release_json.setdefault("tender", {})
        
        # Merge items (Lots)
        if "items" in place_performance_country_code_data["tender"]:
            existing_items = tender.setdefault("items", [])
            for new_item in place_performance_country_code_data["tender"]["items"]:
                existing_item = next((item for item in existing_items if item["relatedLot"] == new_item["relatedLot"]), None)
                if existing_item:
                    existing_item.setdefault("deliveryAddresses", []).extend(new_item["deliveryAddresses"])
                else:
                    existing_items.append(new_item)
        
        # Merge deliveryAddresses (Part and Procedure)
        if "deliveryAddresses" in place_performance_country_code_data["tender"]:
            existing_addresses = tender.setdefault("deliveryAddresses", [])
            for new_address in place_performance_country_code_data["tender"]["deliveryAddresses"]:
                if new_address not in existing_addresses:
                    existing_addresses.append(new_address)
