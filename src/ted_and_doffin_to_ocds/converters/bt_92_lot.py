# converters/bt_92_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_electronic_ordering(xml_content):
    """
    Parse the XML content to extract the electronic ordering information for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed electronic ordering data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "contractTerms": {
                                  "hasElectronicOrdering": bool
                              }
                          }
                      ]
                  }
              }
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

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

    lots = root.xpath("//cac:ProcurementProjectLot", namespaces=namespaces)

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        electronic_ordering = lot.xpath(
            "cac:TenderingTerms/cac:PostAwardProcess/cbc:ElectronicOrderUsageIndicator/text()",
            namespaces=namespaces,
        )

        if lot_id and electronic_ordering:
            lot_data = {
                "id": lot_id[0],
                "contractTerms": {
                    "hasElectronicOrdering": electronic_ordering[0].lower() == "true",
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_electronic_ordering(release_json, electronic_ordering_data) -> None:
    """
    Merge the parsed electronic ordering data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        electronic_ordering_data (dict): The parsed electronic ordering data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not electronic_ordering_data:
        logger.warning("No electronic ordering data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in electronic_ordering_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"],
            )
        else:
            lots.append(new_lot)

    logger.info(
        "Merged electronic ordering data for %d lots",
        len(electronic_ordering_data["tender"]["lots"]),
    )
