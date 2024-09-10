# converters/OPP_031_Tender.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_contract_conditions(xml_content):
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
        lot_id_elements = lot_tender.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces
        )
        if not lot_id_elements:
            logger.warning("Lot ID not found for a LotTender")
            continue
        lot_id = lot_id_elements[0]

        contract_terms = {}
        contract_term_elements = lot_tender.xpath(
            "efac:ContractTerm[efbc:TermCode/@listName='contract-detail']",
            namespaces=namespaces,
        )

        for term in contract_term_elements:
            term_code = term.xpath("efbc:TermCode/text()", namespaces=namespaces)
            term_description = term.xpath(
                "efbc:TermDescription/text()", namespaces=namespaces
            )

            if term_code and term_description and term_code[0] != "all-rev-tic":
                if term_code[0] == "exc-right":
                    contract_terms["hasExclusiveRights"] = True
                elif term_code[0] == "cost-comp":
                    contract_terms["financialTerms"] = term_description[0]
                elif term_code[0] == "other":
                    contract_terms["otherTerms"] = term_description[0]
                elif term_code[0] == "publ-ser-obl":
                    contract_terms["performanceTerms"] = term_description[0]
                elif term_code[0] == "soc-stand":
                    contract_terms["socialStandards"] = term_description[0]

        if contract_terms:
            result["tender"]["lots"].append(
                {"id": lot_id, "contractTerms": contract_terms}
            )

    return result if result["tender"]["lots"] else None


def merge_contract_conditions(release_json, contract_conditions_data):
    if not contract_conditions_data:
        logger.warning("No Contract Conditions data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in contract_conditions_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]), None
        )
        if existing_lot:
            existing_lot.setdefault("contractTerms", {}).update(
                new_lot["contractTerms"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        f"Merged Contract Conditions for {len(contract_conditions_data['tender']['lots'])} lots"
    )
