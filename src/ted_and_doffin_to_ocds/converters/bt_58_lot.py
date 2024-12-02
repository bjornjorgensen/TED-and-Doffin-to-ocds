# converters/bt_58_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_renewal_maximum(xml_content: str | bytes) -> dict | None:
    """Parse maximum number of renewals from XML content for lots.

    This function extracts the maximum number of times the contract can be renewed from
    ProcurementProjectLot elements in the XML.

    Args:
        xml_content: XML string or bytes containing procurement data

    Returns:
        Dict containing OCDS formatted data with lots information, or None if no relevant data found.
        Format:
        {
            "tender": {
                "lots": [{
                    "id": str,
                    "renewal": {
                        "maximumRenewals": int
                    }
                }]
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

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:ProcurementProject/cac:ContractExtension/cbc:MaximumNumberNumeric"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info("No renewal maximum data found. Skipping parse_renewal_maximum.")
        return None

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        max_renewals = lot_element.xpath(
            "./cac:ProcurementProject/cac:ContractExtension/cbc:MaximumNumberNumeric/text()",
            namespaces=namespaces,
        )

        if max_renewals:
            lot_data = {
                "id": lot_id,
                "renewal": {"maximumRenewals": int(max_renewals[0])},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_renewal_maximum(release_json: dict, renewal_data: dict | None) -> None:
    """Merge maximum renewals data into an existing OCDS release.

    Updates the lots in the release_json with maximum renewals information.

    Args:
        release_json: The OCDS release to be updated
        renewal_data: Data containing maximum renewals information to be merged.
                     Expected to have the same structure as parse_renewal_maximum output.

    Returns:
        None. Updates release_json in place.
    """
    if not renewal_data:
        logger.info("No renewal maximum data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in renewal_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("renewal", {}).update(new_lot["renewal"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged renewal maximum data for %d lots",
        len(renewal_data["tender"]["lots"]),
    )
