# converters/OPP_034_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_penalties_and_rewards(xml_content):
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

    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender", namespaces=namespaces
    )
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()", namespaces=namespaces
        )
        if tender_id:
            # Find the corresponding LotResult to get the lot_id
            lot_result = root.xpath(
                f"//efac:NoticeResult/efac:LotResult[efac:LotTender/cbc:ID[@schemeName='tender'] = '{tender_id[0]}']",
                namespaces=namespaces,
            )
            if lot_result:
                lot_id = lot_result[0].xpath(
                    "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                    namespaces=namespaces,
                )
                if lot_id:
                    penalties = lot_tender.xpath(
                        "efac:ContractTerm/efac:FinancialPerformanceRequirement[efbc:FinancialPerformanceTypeCode='penalty']/efbc:FinancialPerformanceDescription/text()",
                        namespaces=namespaces,
                    )
                    rewards = lot_tender.xpath(
                        "efac:ContractTerm/efac:FinancialPerformanceRequirement[efbc:FinancialPerformanceTypeCode='reward']/efbc:FinancialPerformanceDescription/text()",
                        namespaces=namespaces,
                    )

                    if penalties or rewards:
                        lot_data = {
                            "id": lot_id[0],
                            "penaltiesAndRewards": {
                                "penalties": penalties,
                                "rewards": rewards,
                            },
                        }
                        result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_penalties_and_rewards(release_json, penalties_and_rewards_data):
    if not penalties_and_rewards_data:
        logger.warning("No penalties and rewards data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in penalties_and_rewards_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_lot["penaltiesAndRewards"] = new_lot["penaltiesAndRewards"]
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged penalties and rewards data for {len(penalties_and_rewards_data['tender']['lots'])} lots"
    )
