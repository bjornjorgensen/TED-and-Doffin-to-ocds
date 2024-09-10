# converters/OPP_022_Contract.py

from lxml import etree


def map_asset_significance(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"lots": []}}

    settled_contracts = root.xpath(
        "//efac:NoticeResult/efac:SettledContract", namespaces=namespaces
    )

    for contract in settled_contracts:
        contract_id = contract.xpath(
            "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces
        )[0]
        assets = contract.xpath(
            "efac:DurationJustification/efac:AssetsList/efac:Asset",
            namespaces=namespaces,
        )

        if assets:
            lot_results = root.xpath(
                f"//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract'] = '{contract_id}']",
                namespaces=namespaces,
            )

            for lot_result in lot_results:
                lot_id = lot_result.xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=namespaces,
                )[0]

                lot = {"id": lot_id, "essentialAssets": []}

                for asset in assets:
                    asset_significance = asset.xpath(
                        "efbc:AssetSignificance/text()", namespaces=namespaces
                    )
                    if asset_significance:
                        lot["essentialAssets"].append(
                            {"significance": asset_significance[0]}
                        )

                if lot[
                    "essentialAssets"
                ]:  # Only add the lot if it has essential assets
                    result["tender"]["lots"].append(lot)

    return result


def merge_asset_significance(release_json, asset_significance_data):
    if not asset_significance_data.get("tender", {}).get("lots"):
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in asset_significance_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_assets = existing_lot.setdefault("essentialAssets", [])
            for new_asset in new_lot.get("essentialAssets", []):
                if new_asset not in existing_assets:
                    existing_assets.append(new_asset)
        else:
            existing_lots.append(new_lot)
