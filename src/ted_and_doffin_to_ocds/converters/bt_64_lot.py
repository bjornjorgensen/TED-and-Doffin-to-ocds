# converters/bt_64_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_subcontracting_obligation_minimum(xml_content: bytes):
    """
    Parse the XML content to extract the subcontracting obligation minimum percentage for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed subcontracting obligation minimum data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "subcontractingTerms": {
                                  "competitiveMinimumPercentage": float_value
                              }
                          }
                      ]
                  }
              }
        None: If no relevant data is found.

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
        minimum_percent = lot.xpath(
            "cac:TenderingTerms/cac:AllowedSubcontractTerms[cbc:SubcontractingConditionsCode/@listName='subcontracting-obligation']/cbc:MinimumPercent/text()",
            namespaces=namespaces,
        )

        if minimum_percent:
            try:
                competitive_minimum_percentage = float(minimum_percent[0]) / 100
                lot_data = {
                    "id": lot_id,
                    "subcontractingTerms": {
                        "competitiveMinimumPercentage": competitive_minimum_percentage,
                    },
                }
                result["tender"]["lots"].append(lot_data)
            except ValueError:
                logger.warning(
                    "Invalid minimum percentage value for lot %s: %s",
                    lot_id,
                    minimum_percent[0],
                )

    return result if result["tender"]["lots"] else None


def merge_subcontracting_obligation_minimum(
    release_json,
    subcontracting_obligation_minimum_data,
):
    """
    Merge the parsed subcontracting obligation minimum data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        subcontracting_obligation_minimum_data (dict): The parsed subcontracting obligation minimum data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not subcontracting_obligation_minimum_data:
        logger.warning("No subcontracting obligation minimum data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in subcontracting_obligation_minimum_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("subcontractingTerms", {}).update(
                new_lot["subcontractingTerms"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged subcontracting obligation minimum data for %d lots",
        len(subcontracting_obligation_minimum_data["tender"]["lots"]),
    )
