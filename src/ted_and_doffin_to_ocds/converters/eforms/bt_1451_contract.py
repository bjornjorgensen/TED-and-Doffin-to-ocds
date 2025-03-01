# converters/bt_1451_Contract.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_winner_decision_date(xml_content: str | bytes) -> dict | None:
    """Parse winner decision date information from XML content following BT-1451.

    Extracts award dates from settled contracts and maps them to corresponding lot results.
    Converts dates to ISO format using end_date for standardization.

    Args:
        xml_content: XML string or bytes containing the notice result data

    Returns:
        Optional[Dict]: Dictionary containing awards with dates, or None if no awards found
        Format: {"awards": [{"id": str, "date": str}]}

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

    result = {"awards": []}

    notice_results = root.xpath("//efac:NoticeResult", namespaces=namespaces)

    for notice_result in notice_results:
        settled_contracts = notice_result.xpath(
            "efac:SettledContract",
            namespaces=namespaces,
        )
        lot_results = notice_result.xpath("efac:LotResult", namespaces=namespaces)

        for settled_contract in settled_contracts:
            contract_id = settled_contract.xpath(
                "cbc:ID[@schemeName='contract']/text()",
                namespaces=namespaces,
            )
            award_date = settled_contract.xpath(
                "cbc:AwardDate/text()",
                namespaces=namespaces,
            )

            if contract_id and award_date:
                contract_id = contract_id[0]
                award_date = end_date(award_date[0])

                for lot_result in lot_results:
                    lot_contract_id = lot_result.xpath(
                        "efac:SettledContract/cbc:ID[@schemeName='contract']/text()",
                        namespaces=namespaces,
                    )
                    lot_result_id = lot_result.xpath(
                        "cbc:ID[@schemeName='result']/text()",
                        namespaces=namespaces,
                    )

                    if (
                        lot_contract_id
                        and lot_contract_id[0] == contract_id
                        and lot_result_id
                    ):
                        award = {"id": lot_result_id[0], "date": award_date}
                        result["awards"].append(award)

    return result if result["awards"] else None


def merge_winner_decision_date(
    release_json: dict, winner_decision_date_data: dict | None
) -> None:
    """Merge winner decision date data into the release JSON.

    Updates or adds award dates in the release JSON document.
    Only updates existing award dates if the new date is earlier.

    Args:
        release_json: The target release JSON document to update
        winner_decision_date_data: The winner decision date data to merge

    Returns:
        None: Modifies release_json in place

    """
    if not winner_decision_date_data:
        logger.warning("No Winner Decision Date data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in winner_decision_date_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            if (
                "date" not in existing_award
                or new_award["date"] < existing_award["date"]
            ):
                existing_award["date"] = new_award["date"]
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged Winner Decision Date data for %d awards",
        len(winner_decision_date_data["awards"]),
    )
