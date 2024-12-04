# converters/bt_717_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_clean_vehicles_directive(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the clean vehicles directive (BT-717) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed clean vehicles directive data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
                        "coveredBy": [
                            "EU-CVD"
                        ]
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
        applicable_legal_basis = lot.xpath(
            ".//cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:StrategicProcurement/efbc:ApplicableLegalBasis[@listName='cvd-scope']/text()",
            namespaces=namespaces,
        )

        if applicable_legal_basis and applicable_legal_basis[0].lower() == "true":
            lot_data = {"id": lot_id, "coveredBy": ["EU-CVD"]}
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_clean_vehicles_directive(
    release_json: dict[str, Any],
    clean_vehicles_directive_data: dict[str, Any] | None,
) -> None:
    """Merge clean vehicles directive data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        clean_vehicles_directive_data: The clean vehicles directive data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not clean_vehicles_directive_data:
        logger.warning("No Clean Vehicles Directive data to merge")
        return

    tender = release_json.setdefault("tender", {})
    release_lots = tender.setdefault("lots", [])

    cvd_lots = {
        lot["id"]: lot for lot in clean_vehicles_directive_data["tender"]["lots"]
    }

    for lot in release_lots:
        lot_id = lot["id"]
        if lot_id in cvd_lots:
            lot.setdefault("coveredBy", []).extend(cvd_lots[lot_id]["coveredBy"])

    logger.info(
        "Merged Clean Vehicles Directive data for %d lots",
        len(cvd_lots),
    )
