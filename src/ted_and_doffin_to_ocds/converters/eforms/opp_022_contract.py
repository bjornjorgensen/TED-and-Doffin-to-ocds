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


def parse_asset_significance(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse asset significance information (OPP-022) from XML content.

    Gets asset significance values from each contract and maps them to
    corresponding lots' essential assets array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with asset significance or None if no data found

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
                            significance = asset.xpath(
                                "efbc:AssetSignificance/text()",
                                namespaces=NAMESPACES,
                            )
                            if significance:
                                asset_data.append({"significance": significance[0]})

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
        logger.exception("Error parsing asset significance information")
        return None

    return None


def merge_asset_significance(
    release_json: dict[str, Any], significance_data: dict[str, Any] | None
) -> None:
    """Merge asset significance information into the release JSON.

    Updates or creates lots with essential assets significance values.
    Preserves existing lot data while adding/updating significance information.

    Args:
        release_json: The target release JSON to update
        significance_data: The source data containing significance values to merge

    Returns:
        None

    """
    if not significance_data:
        logger.warning("No asset significance data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in significance_data["tender"]["lots"]:
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
        "Merged asset significance data for %d lots",
        len(significance_data["tender"]["lots"]),
    )
