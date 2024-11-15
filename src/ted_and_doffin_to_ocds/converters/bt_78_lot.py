# converters/bt_78_Lot.py

import logging
from lxml import etree
from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_security_clearance_deadline(xml_content):
    """
    Parse the XML content to extract the Security Clearance Deadline for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "milestones": [
                                  {
                                      "id": "1",
                                      "type": "securityClearanceDeadline",
                                      "dueDate": "iso_formatted_date"
                                  }
                              ]
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
        security_clearance_date = lot.xpath(
            "cac:TenderingTerms/cbc:LatestSecurityClearanceDate/text()",
            namespaces=namespaces,
        )

        if security_clearance_date:
            lot_data = {
                "id": lot_id,
                "milestones": [
                    {
                        "id": "1",
                        "type": "securityClearanceDeadline",
                        "dueDate": end_date(security_clearance_date[0]),
                    },
                ],
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_security_clearance_deadline(release_json, security_clearance_data):
    """
    Merge the parsed Security Clearance Deadline data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        security_clearance_data (dict): The parsed Security Clearance Deadline data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not security_clearance_data:
        logger.warning("No Security Clearance Deadline data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in security_clearance_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_milestones = existing_lot.setdefault("milestones", [])
            existing_milestones.extend(new_lot["milestones"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Security Clearance Deadline data for %d lots",
        len(security_clearance_data["tender"]["lots"]),
    )
