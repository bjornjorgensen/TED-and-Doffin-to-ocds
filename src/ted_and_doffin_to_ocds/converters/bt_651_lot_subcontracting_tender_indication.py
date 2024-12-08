# converters/bt_651_Lot_Subcontracting_Tender_Indication.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontracting_tender_indication(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the subcontracting tender indication (BT-651) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed subcontracting tender indication data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
                        "submissionTerms": {
                            "subcontractingClauses": [
                                "subc-oblig"
                            ]
                        }
                    }
                ]
            }
        }

    """
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

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        subcontracting_code = lot.xpath(
            "cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:TenderSubcontractingRequirements/efbc:TenderSubcontractingRequirementsCode[@listName='subcontracting-indication']/text()",
            namespaces=namespaces,
        )

        if subcontracting_code:
            lot_data = {
                "id": lot_id,
                "submissionTerms": {"subcontractingClauses": subcontracting_code},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_subcontracting_tender_indication(
    release_json: dict[str, Any],
    subcontracting_tender_indication_data: dict[str, Any] | None,
) -> None:
    """Merge subcontracting tender indication data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        subcontracting_tender_indication_data: The subcontracting tender indication data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not subcontracting_tender_indication_data:
        logger.warning("No subcontracting tender indication data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in subcontracting_tender_indication_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            submission_terms = existing_lot.setdefault("submissionTerms", {})
            existing_clauses = submission_terms.setdefault("subcontractingClauses", [])
            existing_clauses.extend(new_lot["submissionTerms"]["subcontractingClauses"])
            # Remove duplicates while preserving order
            submission_terms["subcontractingClauses"] = list(
                dict.fromkeys(existing_clauses),
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged subcontracting tender indication data for %d lots",
        len(subcontracting_tender_indication_data["tender"]["lots"]),
    )
