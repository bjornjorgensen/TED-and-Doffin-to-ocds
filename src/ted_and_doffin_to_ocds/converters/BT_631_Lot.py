# converters/BT_631_Lot.py

import logging
from lxml import etree
from ted_and_doffin_to_ocds.utils.date_utils import convert_to_iso_format

logger = logging.getLogger(__name__)


def parse_dispatch_invitation_interest(xml_content):
    """
    Parse the XML content to extract the dispatch invitation interest date for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed dispatch invitation interest dates in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "communication": {
                                  "invitationToConfirmInterestDispatchDate": "iso_date"
                              }
                          }
                      ]
                  }
              }
        None: If no relevant data is found.
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        dispatch_date = lot.xpath(
            "cac:TenderingProcess/cac:ParticipationInvitationPeriod/cbc:StartDate/text()",
            namespaces=namespaces,
        )

        if dispatch_date:
            iso_date = convert_to_iso_format(dispatch_date[0], is_start_date=True)
            lot_data = {
                "id": lot_id,
                "communication": {"invitationToConfirmInterestDispatchDate": iso_date},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_dispatch_invitation_interest(release_json, dispatch_invitation_data):
    """
    Merge the parsed dispatch invitation interest data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        dispatch_invitation_data (dict): The parsed dispatch invitation interest data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not dispatch_invitation_data:
        logger.warning("No dispatch invitation interest data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in dispatch_invitation_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None,
        )
        if existing_lot:
            existing_lot.setdefault("communication", {}).update(
                new_lot["communication"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged dispatch invitation interest data for {len(dispatch_invitation_data['tender']['lots'])} lots",
    )
