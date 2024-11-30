# converters/bt_7220_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_lot_eu_funds(
    xml_content: str | bytes,
) -> dict[str, list[dict[str, Any]]] | None:
    """
    Parse EU funds programme information for each lot.

    BT-7220-Lot: Programme of Union funds used to finance the contract.
    Maps to .planning.budget.finance[].title for each lot.

    Args:
        xml_content: XML content to parse

    Returns:
        Dictionary with lot data including EU funds info, or None if no data found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        result = {"lots": []}

        # Find all lots
        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)

            # Get all funding programs for this lot
            funding_elements = lot.xpath(
                """cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/
                ext:ExtensionContent/efext:EformsExtension/efac:Funding/
                cbc:FundingProgramCode[@listName='eu-programme']""",
                namespaces=NAMESPACES,
            )

            if lot_id and funding_elements:
                lot_data = {
                    "id": lot_id[0],
                    "planning": {
                        "budget": {
                            "finance": [
                                {
                                    "id": str(
                                        i + 1
                                    ),  # Incremental ID based on position
                                    "title": element.text,
                                }
                                for i, element in enumerate(funding_elements)
                                if element.text and element.text.strip()
                            ]
                        }
                    },
                }

                # Only add lot if it has valid funding data
                if lot_data["planning"]["budget"]["finance"]:
                    result["lots"].append(lot_data)
                    logger.info(
                        "Found %d EU fund(s) for lot %s",
                        len(lot_data["planning"]["budget"]["finance"]),
                        lot_id[0],
                    )

        return result if result["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing lot EU funds data")
        return None


def merge_lot_eu_funds(
    release_json: dict[str, Any],
    lot_eu_funds_data: dict[str, list[dict[str, Any]]] | None,
) -> None:
    """
    Merge EU funds data into release JSON, preserving existing data.

    Args:
        release_json: Target release JSON to update
        lot_eu_funds_data: EU funds data to merge
    """
    if not lot_eu_funds_data:
        logger.debug("No EU funds data to merge")
        return

    # Initialize lots array if it doesn't exist
    if "lots" not in release_json:
        release_json["lots"] = []

    # Process each lot with EU funds data
    for new_lot in lot_eu_funds_data["lots"]:
        # Find existing lot or add new one
        existing_lot = next(
            (lot for lot in release_json["lots"] if lot["id"] == new_lot["id"]),
            None,
        )

        if existing_lot:
            # Ensure planning.budget.finance structure exists
            planning = existing_lot.setdefault("planning", {})
            budget = planning.setdefault("budget", {})
            finance = budget.setdefault("finance", [])

            # Update/append finance entries
            for new_finance in new_lot["planning"]["budget"]["finance"]:
                # Check if finance entry with same ID exists
                existing_finance = next(
                    (f for f in finance if f["id"] == new_finance["id"]), None
                )
                if existing_finance:
                    existing_finance.update(new_finance)
                else:
                    finance.append(new_finance)
        else:
            # Add new lot with EU funds data
            release_json["lots"].append(new_lot)

        logger.info("Merged EU funds data for lot %s", new_lot["id"])
