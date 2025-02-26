"""BT-06-Lot Strategic Procurement converter.

This module handles the conversion of strategic procurement codes to OCDS format.
It maps the strategic procurement codes to corresponding goals and adds required strategies.
"""

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

STRATEGIC_PROCUREMENT_MAPPING = {
    "env-imp": "environmental",
    "inn-pur": "economic.innovativePurchase",
    "soc-obj": "social",
}

# These strategies are always included for any sustainable lot as per eForms spec
DEFAULT_STRATEGIES = [
    "awardCriteria",
    "contractPerformanceConditions",
    "selectionCriteria",
    "technicalSpecifications",
]


def parse_strategic_procurement(xml_content: str | bytes) -> dict | None:
    """Parse strategic procurement information from XML.

    Args:
        xml_content: The XML content to parse

    Returns:
        dict: Dictionary with strategic procurement data per lot
        None: If no strategic procurement data found or if parsing fails
    """
    try:
        root = etree.fromstring(
            xml_content if isinstance(xml_content, bytes) else xml_content.encode()
        )

        result = {"tender": {"lots": []}}

        # Find all lots with proper schemeName attribute
        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            # Get lot ID, ensuring the schemeName attribute is correct
            lot_ids = lot.xpath(
                "cbc:ID[@schemeName='Lot']/text()",
                namespaces=NAMESPACES,
            )
            if not lot_ids:
                logger.warning("Lot found without valid ID, skipping")
                continue

            lot_id = lot_ids[0]

            # Get strategic procurement codes
            codes = lot.xpath(
                "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='strategic-procurement']/cbc:ProcurementTypeCode/text()",
                namespaces=NAMESPACES,
            )

            if not codes:
                continue

            lot_data = {"id": lot_id}
            sustainability_entries = []

            has_non_none_code = False
            for code in codes:
                if code == "none":
                    continue

                goal = STRATEGIC_PROCUREMENT_MAPPING.get(code)
                if goal:
                    has_non_none_code = True
                    sustainability_entries.append(
                        {
                            "goal": goal,
                            "strategies": DEFAULT_STRATEGIES.copy(),
                        }
                    )

            if has_non_none_code:
                lot_data["hasSustainability"] = True
                lot_data["sustainability"] = sustainability_entries
                result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.ParseError:
        logger.exception("Failed to parse XML")
        return None
    except Exception:
        logger.exception("Error processing strategic procurement data")
        return None


def merge_strategic_procurement(
    release_json: dict, strategic_procurement_data: dict | None
) -> None:
    """Merge strategic procurement data into the release JSON.

    Args:
        release_json: The release JSON to merge into
        strategic_procurement_data: Strategic procurement data to merge
    """
    if not strategic_procurement_data:
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in strategic_procurement_data["tender"]["lots"]:
        matching_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if matching_lot:
            matching_lot["hasSustainability"] = new_lot["hasSustainability"]
            matching_lot["sustainability"] = new_lot["sustainability"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Strategic Procurement data for %d lots",
        len(strategic_procurement_data["tender"]["lots"]),
    )
