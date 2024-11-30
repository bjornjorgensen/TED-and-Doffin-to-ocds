# converters/bt_46_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_jury_member_name(xml_content):
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

    # Check if the relevant XPath exists
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']//cac:AwardingTerms/cac:TechnicalCommitteePerson/cbc:FamilyName"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info("No jury member data found. Skipping parse_jury_member_name.")
        return None

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        jury_members = lot_element.xpath(
            ".//cac:AwardingTerms/cac:TechnicalCommitteePerson/cbc:FamilyName/text()",
            namespaces=namespaces,
        )

        if jury_members:
            lot = {
                "id": lot_id,
                "designContest": {
                    "juryMembers": [{"name": name} for name in jury_members],
                },
            }
            result["tender"]["lots"].append(lot)

    return result if result["tender"]["lots"] else None


def merge_jury_member_name(release_json, jury_member_data) -> None:
    if not jury_member_data:
        logger.warning("No Jury Member Name data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in jury_member_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_design_contest = existing_lot.setdefault("designContest", {})
            existing_jury_members = existing_design_contest.setdefault(
                "juryMembers",
                [],
            )
            existing_jury_members.extend(new_lot["designContest"]["juryMembers"])
        else:
            tender_lots.append(new_lot)

    logger.info(
        "Merged Jury Member Name data for %d lots",
        len(jury_member_data["tender"]["lots"]),
    )
