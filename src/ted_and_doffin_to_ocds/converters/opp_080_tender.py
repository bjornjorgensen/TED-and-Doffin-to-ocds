# converters/OPP_080_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_kilometers_public_transport(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"contracts": []}

    lot_tenders = root.xpath(
        "//efac:noticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath(
            "cbc:ID[@schemeName='tender']/text()",
            namespaces=namespaces,
        )
        kilometers = lot_tender.xpath(
            "efbc:PublicTransportationCumulatedDistance/text()",
            namespaces=namespaces,
        )

        if tender_id and kilometers:
            tender_id = tender_id[0]
            kilometers = int(kilometers[0])

            settled_contract = root.xpath(
                f"//efac:noticeResult/efac:SettledContract[efac:LotTender/cbc:ID[@schemeName='tender']/text()='{tender_id}']",
                namespaces=namespaces,
            )

            if settled_contract:
                contract_id = settled_contract[0].xpath(
                    "cbc:ID[@schemeName='contract']/text()",
                    namespaces=namespaces,
                )
                lot_result = root.xpath(
                    f"//efac:noticeResult/efac:LotResult[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id[0]}']",
                    namespaces=namespaces,
                )

                if contract_id and lot_result:
                    award_id = lot_result[0].xpath(
                        "cbc:ID[@schemeName='result']/text()",
                        namespaces=namespaces,
                    )

                    contract = {
                        "id": contract_id[0],
                        "publicPassengerTransportServicesKilometers": kilometers,
                        "awardID": award_id[0] if award_id else None,
                    }
                    result["contracts"].append(contract)

    return result if result["contracts"] else None


def merge_kilometers_public_transport(release_json, kilometers_data):
    if not kilometers_data:
        logger.warning("No Kilometers Public Transport data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in kilometers_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_contract.update(new_contract)
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged Kilometers Public Transport data for %d contracts",
        len(kilometers_data["contracts"]),
    )
