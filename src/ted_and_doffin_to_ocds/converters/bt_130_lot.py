# converters/bt_130_Lot.py

import logging
from lxml import etree
from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_dispatch_invitation_tender(xml_content):
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
        invitation_date = lot.xpath(
            "cac:TenderingProcess/cac:InvitationSubmissionPeriod/cbc:StartDate/text()",
            namespaces=namespaces,
        )

        if invitation_date:
            try:
                iso_date = start_date(invitation_date[0])
                result["tender"]["lots"].append(
                    {"id": lot_id, "secondStage": {"invitationDate": iso_date}},
                )
            except ValueError:
                logger.exception("Error parsing invitation date for lot %s", lot_id)

    return result if result["tender"]["lots"] else None


def merge_dispatch_invitation_tender(release_json, dispatch_invitation_data):
    if not dispatch_invitation_data:
        logger.warning("No Dispatch Invitation Tender data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in dispatch_invitation_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("secondStage", {}).update(new_lot["secondStage"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Dispatch Invitation Tender data for %d lots",
        len(dispatch_invitation_data["tender"]["lots"]),
    )
