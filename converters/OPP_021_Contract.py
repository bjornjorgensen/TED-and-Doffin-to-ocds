# converters/OPP_021_Contract.py

from lxml import etree

def map_essential_assets(xml_content):
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
        assets = contract.xpath("efac:DurationJustification/efac:AssetsList/efac:Asset", namespaces=namespaces)
        
        if assets:
            lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id}']", namespaces=namespaces)
            
            for lot_result in lot_results:
                lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)[0]
                
                lot = {
                    "id": lot_id,
                    "essentialAssets": []
                }
                
                for asset in assets:
                    asset_description = asset.xpath("efbc:AssetDescription/text()", namespaces=namespaces)
                    if asset_description:
                        lot["essentialAssets"].append({"description": asset_description[0]})
                
                if lot["essentialAssets"]:  # Only add the lot if it has essential assets
                    result["tender"]["lots"].append(lot)

    return result

def merge_essential_assets(release_json, essential_assets_data):
    if not essential_assets_data.get("tender", {}).get("lots"):
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in essential_assets_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_assets = existing_lot.setdefault("essentialAssets", [])
            for new_asset in new_lot.get("essentialAssets", []):
                if new_asset not in existing_assets:
                    existing_assets.append(new_asset)
        else:
            existing_lots.append(new_lot)