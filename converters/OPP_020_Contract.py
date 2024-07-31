# converters/OPP_020_Contract.py

from lxml import etree

def map_extended_duration_indicator(xml_content):
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

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    
    for contract in settled_contracts:
        contract_id = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)[0]
        extended_duration = contract.xpath("efac:DurationJustification/efbc:ExtendedDurationIndicator/text()", namespaces=namespaces)
        
        if extended_duration:
            extended_duration = extended_duration[0].lower() == 'true'
            
            lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id}']", namespaces=namespaces)
            
            for lot_result in lot_results:
                lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='lot']/text()", namespaces=namespaces)[0]
                
                lot = {
                    "id": lot_id,
                    "hasEssentialAssets": extended_duration
                }
                result["tender"]["lots"].append(lot)

    return result

def merge_extended_duration_indicator(release_json, extended_duration_data):
    if not extended_duration_data["tender"]["lots"]:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in extended_duration_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot["hasEssentialAssets"] = new_lot["hasEssentialAssets"]
        else:
            existing_lots.append(new_lot)