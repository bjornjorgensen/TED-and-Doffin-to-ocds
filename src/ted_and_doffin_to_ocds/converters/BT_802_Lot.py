# converters/BT_802_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_non_disclosure_agreement_description(xml_content):
    logger.info("Parsing BT-802-Lot: Non Disclosure Agreement Description")
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

    lot_elements = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    logger.debug(f"Found {len(lot_elements)} lot elements")

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        nda_description = lot.xpath(
            "cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='nda']/cbc:Description/text()",
            namespaces=namespaces,
        )

        if nda_description:
            logger.debug(f"Lot {lot_id} has NDA description: {nda_description[0]}")
            result["tender"]["lots"].append(
                {
                    "id": lot_id,
                    "contractTerms": {"nonDisclosureAgreement": nda_description[0]},
                }
            )
        else:
            logger.debug(f"No NDA description found for lot {lot_id}")

    logger.info(f"Parsed NDA descriptions for {len(result['tender']['lots'])} lots")
    return result


def merge_non_disclosure_agreement_description(release_json, nda_description_data):
    logger.info("Merging BT-802-Lot: Non Disclosure Agreement Description")
    if not nda_description_data["tender"]["lots"]:
        logger.warning("No NDA description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for nda_lot in nda_description_data["tender"]["lots"]:
        lot_id = nda_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)

        if existing_lot:
            existing_lot.setdefault("contractTerms", {})["nonDisclosureAgreement"] = (
                nda_lot["contractTerms"]["nonDisclosureAgreement"]
            )
            logger.debug(f"Updated NDA description for existing lot {lot_id}")
        else:
            lots.append(nda_lot)
            logger.debug(f"Added new lot {lot_id} with NDA description")

    logger.info(
        f"Merged NDA descriptions for {len(nda_description_data['tender']['lots'])} lots"
    )
