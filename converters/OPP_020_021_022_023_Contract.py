# converters/OPP_020_021_022_023_Contract.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_essential_assets(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"tender": {"lots": []}}

    settled_contracts = root.xpath("//efac:NoticeResult/efac:SettledContract", namespaces=namespaces)
    for contract in settled_contracts:
        contract_id_elements = contract.xpath("cbc:ID[@schemeName='contract']/text()", namespaces=namespaces)
        if not contract_id_elements:
            logger.warning("Contract ID not found for a SettledContract")
            continue
        contract_id = contract_id_elements[0]

        # OPP-020-Contract
        extended_duration = contract.xpath("efac:DurationJustification/efbc:ExtendedDurationIndicator/text()", namespaces=namespaces)
        has_essential_assets = extended_duration[0].lower() == 'true' if extended_duration else None

        # OPP-021-022-023-Contract
        assets = contract.xpath("efac:DurationJustification/efac:AssetsList/efac:Asset", namespaces=namespaces)
        essential_assets = []
        for asset in assets:
            asset_data = {}
            description = asset.xpath("efbc:AssetDescription/text()", namespaces=namespaces)
            if description:
                asset_data["description"] = description[0]

            significance = asset.xpath("efbc:AssetSignificance/text()", namespaces=namespaces)
            if significance:
                asset_data["significance"] = significance[0]

            predominance = asset.xpath("efbc:AssetPredominance/text()", namespaces=namespaces)
            if predominance:
                asset_data["predominance"] = predominance[0]

            if asset_data:
                essential_assets.append(asset_data)

        lot_results = root.xpath(f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']", namespaces=namespaces)
        for lot_result in lot_results:
            lot_id_elements = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
            if not lot_id_elements:
                logger.warning(f"Lot ID not found for contract {contract_id}")
                continue
            lot_id = lot_id_elements[0]
            
            lot_data = {
                "id": lot_id
            }
            if has_essential_assets is not None:
                lot_data["hasEssentialAssets"] = has_essential_assets
            if essential_assets:
                lot_data["essentialAssets"] = essential_assets
            
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_essential_assets(release_json, essential_assets_data):
    if not essential_assets_data:
        logger.warning("No Essential Assets data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in essential_assets_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            if "hasEssentialAssets" in new_lot:
                existing_lot["hasEssentialAssets"] = new_lot["hasEssentialAssets"]
            if "essentialAssets" in new_lot:
                existing_lot["essentialAssets"] = new_lot["essentialAssets"]
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Essential Assets for {len(essential_assets_data['tender']['lots'])} lots")