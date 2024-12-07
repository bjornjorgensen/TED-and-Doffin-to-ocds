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


def parse_revenues_allocation(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse revenues allocation information (OPP-032) from XML content.

    This mapping assumes that revenue percentages are consistent across all lot tenders
    for a given lot. Contact OCDS Data Support Team if values vary per lot tender.

    Gets revenue sharing percentage for each lot tender and maps it to
    corresponding lot's contractTerms.operatorRevenueShare as decimal.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing lots with revenue allocation or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lot_tenders = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:LotTender",
            namespaces=NAMESPACES,
        )

        lot_revenues = {}
        for lot_tender in lot_tenders:
            try:
                lot_id = lot_tender.xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=NAMESPACES,
                )[0]

                revenue_percent = lot_tender.xpath(
                    "efac:ContractTerm[efbc:TermCode/text()='all-rev-tic']/"
                    "efbc:TermPercent/text()",
                    namespaces=NAMESPACES,
                )

                if revenue_percent:
                    if (
                        lot_id in lot_revenues
                        and lot_revenues[lot_id] != revenue_percent[0]
                    ):
                        logger.warning(
                            "Inconsistent revenue percentages found for lot %s across different tenders. "
                            "Contact OCDS Data Support Team.",
                            lot_id,
                        )
                    lot_revenues[lot_id] = revenue_percent[0]

                    decimal_value = float(revenue_percent[0]) / 100
                    result["tender"]["lots"].append(
                        {
                            "id": lot_id,
                            "contractTerms": {"operatorRevenueShare": decimal_value},
                        }
                    )

            except (IndexError, AttributeError, ValueError) as e:
                logger.warning("Skipping incomplete lot tender data: %s", e)
                continue

        if result["tender"]["lots"]:
            return result

    except Exception:
        logger.exception("Error parsing revenues allocation")
        return None

    return None


def merge_revenues_allocation(
    release_json: dict[str, Any], revenues_data: dict[str, Any] | None
) -> None:
    """
    Merge revenues allocation into the release JSON.

    Updates or creates lots with revenue sharing information.
    Preserves existing lot data while adding/updating revenue share.

    Args:
        release_json: The target release JSON to update
        revenues_data: The source data containing revenue allocation to merge

    Returns:
        None
    """
    if not revenues_data:
        logger.warning("No revenues allocation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in revenues_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged revenues allocation for %d lots",
        len(revenues_data["tender"]["lots"]),
    )
