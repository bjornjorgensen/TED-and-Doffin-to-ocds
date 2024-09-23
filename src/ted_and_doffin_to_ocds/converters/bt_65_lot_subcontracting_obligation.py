# converters/bt_65_Lot_Subcontracting_Obligation.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

SUBCONTRACTING_OBLIGATION_MAPPING = {
    "none": "No subcontracting obligation applies.",
    "subc-chng": "The contractor must indicate any change of subcontractors during the execution of the contract.",
    "subc-min": "The contractor must subcontract a minimum percentage of the contract using the procedure set out in Title III of Directive 2009/81/EC.",
    "subc-oblig-2009-81": "The buyer may oblige the contractor to award all or certain subcontracts through the procedure set out in Title III of Directive 2009/81/EC.",
}


def parse_subcontracting_obligation(xml_content: bytes):
    """
    Parse the XML content to extract the subcontracting obligation for each lot.

    Args:
        xml_content (bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed subcontracting obligation data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "subcontractingTerms": {
                                  "description": "obligation description"
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
        subcontracting_code = lot.xpath(
            "cac:TenderingTerms/cac:AllowedSubcontractTerms[cbc:SubcontractingConditionsCode/@listName='subcontracting-obligation']/cbc:SubcontractingConditionsCode/text()",
            namespaces=namespaces,
        )

        if subcontracting_code and subcontracting_code[0] != "none":
            description = SUBCONTRACTING_OBLIGATION_MAPPING.get(subcontracting_code[0])
            if description:
                lot_data = {
                    "id": lot_id,
                    "subcontractingTerms": {"description": description},
                }
                result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_subcontracting_obligation(release_json, subcontracting_obligation_data):
    """
    Merge the parsed subcontracting obligation data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        subcontracting_obligation_data (dict): The parsed subcontracting obligation data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not subcontracting_obligation_data:
        logger.warning("No subcontracting obligation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in subcontracting_obligation_data["tender"]["lots"]:
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
        f"Merged subcontracting obligation data for {len(subcontracting_obligation_data['tender']['lots'])} lots",
    )
