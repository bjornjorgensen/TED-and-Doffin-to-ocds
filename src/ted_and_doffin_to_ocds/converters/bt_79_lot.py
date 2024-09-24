# converters/bt_79_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_performing_staff_qualification(xml_content):
    """
    Parse the XML content to extract the Performing Staff Qualification requirement for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "otherRequirements": {
                                  "requiresStaffNamesAndQualifications": boolean
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

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        required_curricula_code = lot.xpath(
            "cac:TenderingTerms/cbc:RequiredCurriculaCode/text()",
            namespaces=namespaces,
        )

        if required_curricula_code:
            code = required_curricula_code[0]
            if code in ["par-requ", "t-requ"]:
                requires_staff = True
            elif code == "not-requ":
                requires_staff = False
            else:
                continue  # Discard if not one of the specified codes

            lot_data = {
                "id": lot_id,
                "otherRequirements": {
                    "requiresStaffNamesAndQualifications": requires_staff,
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_performing_staff_qualification(release_json, staff_qualification_data):
    """
    Merge the parsed Performing Staff Qualification data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        staff_qualification_data (dict): The parsed Performing Staff Qualification data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not staff_qualification_data:
        logger.warning("No Performing Staff Qualification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in staff_qualification_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("otherRequirements", {}).update(
                new_lot["otherRequirements"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Performing Staff Qualification data for %d lots",
        len(staff_qualification_data["tender"]["lots"]),
    )
