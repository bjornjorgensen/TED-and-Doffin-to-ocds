import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_asset_predominance(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse asset predominance information (OPP-023) from XML content.

    Gets asset predominance values from each contract and maps them to
    corresponding lots' essential assets array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with asset predominance or None if no data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        settled_contracts = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:SettledContract",
            namespaces=NAMESPACES,
        )

        for contract in settled_contracts:
            try:
                contract_id = contract.xpath(
                    "cbc:ID[@schemeName='contract']/text()",
                    namespaces=NAMESPACES,
                )[0]

                assets = contract.xpath(
                    "efac:DurationJustification/efac:AssetsList/efac:Asset",
                    namespaces=NAMESPACES,
                )

                if assets:
                    lot_results = root.xpath(
                        f"/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
                        f"efext:EformsExtension/efac:NoticeResult/efac:LotResult"
                        f"[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']",
                        namespaces=NAMESPACES,
                    )

                    for lot_result in lot_results:
                        lot_id = lot_result.xpath(
                            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                            namespaces=NAMESPACES,
                        )[0]

                        asset_data = []
                        for asset in assets:
                            predominance_elements = asset.xpath(
                                "efbc:AssetPredominance",
                                namespaces=NAMESPACES,
                            )

                            for predominance_element in predominance_elements:
                                asset_info = {"predominance": predominance_element.text}

                                # Extract languageID attribute if present
                                language_id = predominance_element.get("languageID")
                                if language_id:
                                    asset_info["languageID"] = language_id

                                asset_data.append(asset_info)

                        if asset_data:
                            result["tender"]["lots"].append(
                                {"id": lot_id, "essentialAssets": asset_data}
                            )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete contract data: %s", e)
                continue

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing asset predominance information")
        return None

    return None


def merge_asset_predominance(
    release_json: dict[str, Any], predominance_data: dict[str, Any] | None
) -> None:
    """Merge asset predominance information into the release JSON.

    Updates or creates lots with essential assets predominance values.
    Preserves existing lot data while adding/updating predominance information.

    Args:
        release_json: The target release JSON to update
        predominance_data: The source data containing predominance values to merge

    Returns:
        None

    """
    if not predominance_data:
        logger.warning("No asset predominance data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in predominance_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_assets = existing_lot.setdefault("essentialAssets", [])
            for new_asset in new_lot["essentialAssets"]:
                if new_asset not in existing_assets:
                    existing_assets.append(new_asset)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged asset predominance data for %d lots",
        len(predominance_data["tender"]["lots"]),
    )
