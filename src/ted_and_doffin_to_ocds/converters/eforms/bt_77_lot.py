# converters/bt_77_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_financial_terms(xml_content: str | bytes) -> dict | None:
    """Parse financial terms from XML for each lot.

    Extract information about financing and payment terms and/or references
    to provisions that govern them as defined in BT-77.

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
                            "financialTerms": str
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

    root: etree._Element = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result: dict[str, dict] = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        financial_terms = lot.xpath(
            "cac:TenderingTerms/cac:PaymentTerms/cbc:Note/text()",
            namespaces=namespaces,
        )

        if financial_terms:
            result["tender"]["lots"].append(
                {"id": lot_id, "contractTerms": {"financialTerms": financial_terms[0]}}
            )

    return result if result["tender"]["lots"] else None


def merge_financial_terms(
    release_json: dict, financial_terms_data: dict | None
) -> None:
    """Merge financial terms data into the OCDS release.

    Updates the release JSON in-place by adding or updating contract terms
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        financial_terms_data: The parsed financial terms data
            in the same format as returned by parse_financial_terms().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not financial_terms_data:
        logger.warning("No financial terms data to merge")
        return

    tender: dict = release_json.setdefault("tender", {})
    existing_lots: list = tender.setdefault("lots", [])

    for new_lot in financial_terms_data["tender"]["lots"]:
        existing_lot: dict | None = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged financial terms data for %d lots",
        len(financial_terms_data["tender"]["lots"]),
    )
