# converters/bt_93_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_electronic_payment(xml_content: str | bytes) -> dict | None:
    """Parse electronic payment information from XML for each lot.

    Extract information about whether electronic payment will be used
    as defined in BT-93.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "contractTerms": {
                            "hasElectronicPayment": bool
                        }
                    }
                ]
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
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
        electronic_payment = lot.xpath(
            "cac:TenderingTerms/cac:PostAwardProcess/cbc:ElectronicPaymentUsageIndicator/text()",
            namespaces=namespaces,
        )

        if electronic_payment:
            lot_data = {
                "id": lot_id,
                "contractTerms": {
                    "hasElectronicPayment": electronic_payment[0].lower() == "true",
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_electronic_payment(
    release_json: dict, electronic_payment_data: dict | None
) -> None:
    """Merge electronic payment data into the OCDS release.

    Updates the release JSON in-place by adding or updating contract terms
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        electronic_payment_data: The parsed electronic payment data
            in the same format as returned by parse_electronic_payment().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not electronic_payment_data:
        logger.warning("No electronic payment data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in electronic_payment_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"],
            )
        else:
            lots.append(new_lot)

    logger.info(
        "Merged electronic payment data for %d lots",
        len(electronic_payment_data["tender"]["lots"]),
    )
