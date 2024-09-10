# converters/BT_1451_Contract.py

import logging
from lxml import etree
from utils.date_utils import end_date

logger = logging.getLogger(__name__)


def parse_winner_decision_date(xml_content):
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
            "efac:SettledContract", namespaces=namespaces
        )
        lot_results = notice_result.xpath("efac:LotResult", namespaces=namespaces)

        for settled_contract in settled_contracts:
            contract_id = settled_contract.xpath(
                "cbc:ID[@schemeName='contract']/text()", namespaces=namespaces
            )
            award_date = settled_contract.xpath(
                "cbc:AwardDate/text()", namespaces=namespaces
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
                        "cbc:ID[@schemeName='result']/text()", namespaces=namespaces
                    )

                    if (
                        lot_contract_id
                        and lot_contract_id[0] == contract_id
                        and lot_result_id
                    ):
                        award = {"id": lot_result_id[0], "date": award_date}
                        result["awards"].append(award)

    return result if result["awards"] else None


def merge_winner_decision_date(release_json, winner_decision_date_data):
    if not winner_decision_date_data:
        logger.warning("No Winner Decision Date data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in winner_decision_date_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]), None
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
        f"Merged Winner Decision Date data for {len(winner_decision_date_data['awards'])} awards"
    )
