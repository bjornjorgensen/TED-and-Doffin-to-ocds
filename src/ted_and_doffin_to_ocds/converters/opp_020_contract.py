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


def parse_extended_duration_indicator(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse extended duration indicator (OPP-020) from XML content.

    Gets contract extension indicator and maps it to corresponding lot's
    hasEssentialAssets field.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with essential assets indicator or None if no data found

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

                extended_duration = contract.xpath(
                    "efac:DurationJustification/efbc:ExtendedDurationIndicator/text()",
                    namespaces=NAMESPACES,
                )

                if extended_duration:
                    has_essential_assets = extended_duration[0].lower() == "true"

                    # Find associated lots through LotResult
                    lot_results = root.xpath(
                        f"/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
                        f"efext:EformsExtension/efac:NoticeResult/efac:LotResult"
                        f"[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']",
                        namespaces=NAMESPACES,
                    )

                    for lot_result in lot_results:
                        lot_id = lot_result.xpath(
                            "efac:TenderLot/cbc:ID[@schemeName='lot']/text()",
                            namespaces=NAMESPACES,
                        )[0]

                        result["tender"]["lots"].append(
                            {"id": lot_id, "hasEssentialAssets": has_essential_assets}
                        )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete contract data: %s", e)
                continue

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing extended duration indicator")
        return None

    return None


def merge_extended_duration_indicator(
    release_json: dict[str, Any], duration_data: dict[str, Any] | None
) -> None:
    """Merge extended duration indicator into the release JSON.

    Updates or creates lots with essential assets indicator.
    Preserves existing lot data while adding/updating indicator.

    Args:
        release_json: The target release JSON to update
        duration_data: The source data containing duration indicators to merge

    Returns:
        None

    """
    if not duration_data:
        logger.warning("No extended duration indicator data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in duration_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["hasEssentialAssets"] = new_lot["hasEssentialAssets"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged extended duration indicator for %d lots",
        len(duration_data["tender"]["lots"]),
    )
