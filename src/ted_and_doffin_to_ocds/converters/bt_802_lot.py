# converters/bt_802_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_nda_description(xml_content: str | bytes) -> dict | None:
    """
    Parse BT-802: Non-disclosure agreement description for lots.

    Extracts additional information about NDA requirements for lots.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "contractTerms": {
                                "nonDisclosureAgreement": str
                            }
                        }
                    ]
                }
            }
        Returns None if no relevant data found or on error
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"lots": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            description = lot.xpath(
                ".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='nda']"
                "/cbc:Description/text()",
                namespaces=NAMESPACES,
            )

            if description:
                nda_text = description[0].strip()
                logger.info("Found NDA description for lot %s: %s", lot_id, nda_text)
                result["tender"]["lots"].append(
                    {
                        "id": lot_id,
                        "contractTerms": {"nonDisclosureAgreement": nda_text},
                    }
                )

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing NDA descriptions")
        return None


def merge_nda_description(release_json: dict, nda_data: dict | None) -> None:
    """
    Merge NDA description data into the release JSON.

    Updates or adds NDA descriptions to lot contract terms.

    Args:
        release_json: Main OCDS release JSON to update
        nda_data: NDA description data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' contractTerms
    """
    if not nda_data:
        logger.warning("No NDA description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in nda_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            contract_terms = existing_lot.setdefault("contractTerms", {})
            contract_terms["nonDisclosureAgreement"] = new_lot["contractTerms"][
                "nonDisclosureAgreement"
            ]
        else:
            lots.append(new_lot)

    logger.info(
        "Merged NDA description data for %d lots", len(nda_data["tender"]["lots"])
    )
