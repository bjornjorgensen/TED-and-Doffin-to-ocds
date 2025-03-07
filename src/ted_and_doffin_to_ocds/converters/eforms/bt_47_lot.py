import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_participant_name(xml_content: str | bytes) -> dict | None:
    """Parse participant names from XML content for design contest lots.

    This function extracts participant names from ProcurementProjectLot elements in the XML
    and creates OCDS formatted data structure with parties and lots information.

    Args:
        xml_content: XML string or bytes containing procurement data

    Returns:
        Dict containing OCDS formatted data with parties and lots, or None if no relevant data found.
        Format:
        {
            "parties": [{"id": str, "name": str, "roles": list[str]}],
            "tender": {
                "lots": [{
                    "id": str,
                    "designContest": {
                        "selectedParticipants": [{"id": str, "name": str}]
                    }
                }]
            }
        }

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

    # Check if the relevant XPath exists
    relevant_xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:EconomicOperatorShortList/cac:PreSelectedParty/cac:PartyName/cbc:Name"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info("No participant name data found. Skipping parse_participant_name.")
        return None

    result = {"parties": [], "tender": {"lots": []}}
    party_id_counter = 1

    lot_elements = root.xpath(
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        participant_names = lot_element.xpath(
            ".//cac:TenderingTerms/cac:EconomicOperatorShortList/cac:PreSelectedParty/cac:PartyName/cbc:Name/text()",
            namespaces=namespaces,
        )

        if participant_names:
            lot = {"id": lot_id, "designContest": {"selectedParticipants": []}}

            for name in participant_names:
                party_id = str(party_id_counter)
                party_id_counter += 1

                party = {"id": party_id, "name": name, "roles": ["selectedParticipant"]}
                result["parties"].append(party)

                lot["designContest"]["selectedParticipants"].append(
                    {"id": party_id, "name": name},
                )

            result["tender"]["lots"].append(lot)

    return result if result["parties"] else None


def merge_participant_name(release_json: dict, participant_data: dict | None) -> None:
    """Merge participant name data into an existing OCDS release.

    Updates the parties and lots in the release_json with new participant information.
    Merges roles for existing parties and adds selectedParticipants to existing lots.

    Args:
        release_json: The OCDS release to be updated
        participant_data: Data containing new participant information to be merged.
                        Expected to have the same structure as parse_participant_name output.

    Returns:
        None. Updates release_json in place.

    """
    if not participant_data:
        logger.info("No participant Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_party in participant_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party["roles"] = list(
                set(existing_party.get("roles", []) + new_party["roles"]),
            )
        else:
            existing_parties.append(new_party)

    for new_lot in participant_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_design_contest = existing_lot.setdefault("designContest", {})
            existing_selected_participants = existing_design_contest.setdefault(
                "selectedParticipants",
                [],
            )
            for new_participant in new_lot["designContest"]["selectedParticipants"]:
                if new_participant not in existing_selected_participants:
                    existing_selected_participants.append(new_participant)
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged participant Name data for %d parties and %d lots",
        len(participant_data["parties"]),
        len(participant_data["tender"]["lots"]),
    )
