import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tenderer_legal_form(xml_content: str | bytes) -> dict | None:
    """Parse tenderer legal form requirements from XML for each lot.

    Extract information about the legal form that must be taken by a group
    of tenderers that is awarded a contract as defined in BT-76.

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
                            "tendererLegalForm": str or {language_code: str}
                        }
                    }
                ]
            }
        }
        Returns None if no relevant data is found.
        For multilingual text, tendererLegalForm will be an object with language codes as keys.

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

    result: dict[str, dict[str, list]] = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        legal_form_elements = lot.xpath(
            "cac:TenderingTerms/cac:TendererQualificationRequest[not(cac:SpecificTendererRequirement)]/cbc:CompanyLegalForm",
            namespaces=namespaces,
        )

        if legal_form_elements:
            lot_data = {"id": lot_id, "contractTerms": {}}

            # Handle potential multilingual text
            if (
                len(legal_form_elements) == 1
                and legal_form_elements[0].get("languageID") is None
            ):
                # Single language without specified languageID
                lot_data["contractTerms"]["tendererLegalForm"] = legal_form_elements[
                    0
                ].text
            else:
                # Multiple languages or single with languageID
                multilingual_text = {}
                for element in legal_form_elements:
                    language = element.get(
                        "languageID", "und"
                    )  # 'und' for undefined language
                    multilingual_text[language] = element.text
                lot_data["contractTerms"]["tendererLegalForm"] = multilingual_text

            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_tenderer_legal_form(
    release_json: dict, tenderer_legal_form_data: dict | None
) -> None:
    """Merge tenderer legal form data into the OCDS release.

    Updates the release JSON in-place by adding or updating contract terms
    for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        tenderer_legal_form_data: The parsed legal form data
            in the same format as returned by parse_tenderer_legal_form().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not tenderer_legal_form_data:
        logger.info("No Tenderer Legal Form data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in tenderer_legal_form_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"],
            )
        else:
            tender_lots.append(new_lot)

    logger.info(
        "Merged Tenderer Legal Form data for %d lots",
        len(tenderer_legal_form_data["tender"]["lots"]),
    )
