# converters/BT_76_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_tenderer_legal_form(xml_content: str | bytes) -> dict | None:
    """
    Parse the XML content to extract the tenderer legal form description for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data, or None if no relevant data is found.
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        legal_form = lot.xpath(
            "cac:TenderingTerms/cac:TendererQualificationRequest[not(cac:SpecificTendererRequirement)]/cbc:CompanyLegalForm/text()",
            namespaces=namespaces,
        )

        if legal_form:
            lot_data = {
                "id": lot_id,
                "contractTerms": {"tendererLegalForm": legal_form[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_tenderer_legal_form(release_json: dict, parsed_data: dict | None) -> None:
    """
    Merge the parsed tenderer legal form data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        parsed_data (Optional[Dict]): The parsed tenderer legal form data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not parsed_data:
        logger.info("No Tenderer Legal Form data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in parsed_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"],
            )
        else:
            tender_lots.append(new_lot)

    logger.info(
        f"Merged Tenderer Legal Form data for {len(parsed_data['tender']['lots'])} lots",
    )
