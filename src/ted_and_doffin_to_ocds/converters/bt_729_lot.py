# converters/bt_729_Lot.py

import logging

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


def parse_lot_subcontracting_obligation_maximum(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse BT-729: Maximum subcontracting percentage for competitive procedure.

    Extracts the maximum percentage of contract value that must be subcontracted
    using competitive procedure from Directive 2009/81/EC.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "subcontractingTerms": {
                                "competitiveMaximumPercentage": float
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            max_percent = lot.xpath(
                "cac:TenderingTerms/cac:AllowedSubcontractTerms[cbc:SubcontractingConditionsCode/@listName='subcontracting-obligation']/cbc:MaximumPercent/text()",
                namespaces=NAMESPACES,
            )

            if max_percent:
                try:
                    percentage = float(max_percent[0]) / 100
                    lot_data = {
                        "id": lot_id,
                        "subcontractingTerms": {
                            "competitiveMaximumPercentage": percentage
                        },
                    }
                    result["tender"]["lots"].append(lot_data)
                    logger.info(
                        "Found max subcontracting percentage %f for lot %s",
                        percentage,
                        lot_id,
                    )
                except ValueError:
                    logger.warning("Invalid percentage value: %s", max_percent[0])

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing subcontracting maximum")
        return None


def merge_lot_subcontracting_obligation_maximum(
    release_json: dict, lot_subcontracting_data: dict | None
) -> None:
    """
    Merge subcontracting obligation maximum data into the release JSON.

    Updates or adds subcontracting terms for lots with maximum percentage values.

    Args:
        release_json: Main OCDS release JSON to update
        lot_subcontracting_data: Subcontracting data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' subcontractingTerms
    """
    if not lot_subcontracting_data:
        logger.warning("No lot subcontracting obligation maximum data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender.setdefault("lots", [])

    for new_lot in lot_subcontracting_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender["lots"] if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("subcontractingTerms", {})
            existing_lot["subcontractingTerms"]["competitiveMaximumPercentage"] = (
                new_lot["subcontractingTerms"]["competitiveMaximumPercentage"]
            )
        else:
            tender["lots"].append(new_lot)

    logger.info(
        "Merged subcontracting obligation maximum data for %d lots",
        len(lot_subcontracting_data["tender"]["lots"]),
    )
