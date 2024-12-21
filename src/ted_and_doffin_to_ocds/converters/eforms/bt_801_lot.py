import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_non_disclosure_agreement(xml_content: str | bytes) -> dict | None:
    """Parse BT-801: Non-disclosure agreement requirement for lots.

    Extracts whether lots require a non-disclosure agreement.

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
                                "hasNonDisclosureAgreement": bool
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
            nda = lot.xpath(
                ".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='nda']"
                "/cbc:ExecutionRequirementCode/text()",
                namespaces=NAMESPACES,
            )

            if nda and nda[0].lower() == "true":
                logger.info("Found NDA requirement for lot %s", lot_id)
                result["tender"]["lots"].append(
                    {"id": lot_id, "contractTerms": {"hasNonDisclosureAgreement": True}}
                )

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing NDA requirements")
        return None


def merge_non_disclosure_agreement(release_json: dict, nda_data: dict | None) -> None:
    """Merge non-disclosure agreement data into the release JSON.

    Updates or adds NDA requirements to lot contract terms.

    Args:
        release_json: Main OCDS release JSON to update
        nda_data: NDA requirement data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' contractTerms

    """
    if not nda_data:
        logger.warning("No NDA requirement data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in nda_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            contract_terms = existing_lot.setdefault("contractTerms", {})
            contract_terms["hasNonDisclosureAgreement"] = True
        else:
            lots.append(new_lot)

    logger.info(
        "Merged NDA requirement data for %d lots", len(nda_data["tender"]["lots"])
    )
