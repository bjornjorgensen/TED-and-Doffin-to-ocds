# converters/bt_744_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_lot_esignature_requirement(xml_content: str | bytes) -> dict | None:
    """Parse BT-744: Electronic signature requirement for lots.

    Extracts whether advanced or qualified electronic signature/seal is required
    for submissions, as defined in EU Regulation No 910/2014.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "lots": [
                        {
                            "id": str,
                            "submissionTerms": {
                                "advancedElectronicSignatureRequired": bool
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
            esignature = lot.xpath(
                ".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='esignature-submission']"
                "/cbc:ExecutionRequirementCode/text()",
                namespaces=NAMESPACES,
            )

            if esignature:
                is_required = esignature[0].lower() == "true"
                logger.info(
                    "Found e-signature requirement %s for lot %s", is_required, lot_id
                )
                lot_data = {
                    "id": lot_id,
                    "submissionTerms": {
                        "advancedElectronicSignatureRequired": is_required
                    },
                }
                result["tender"]["lots"].append(lot_data)

        return result if result["tender"]["lots"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing e-signature requirement")
        return None


def merge_lot_esignature_requirement(
    release_json: dict, esignature_data: dict | None
) -> None:
    """Merge electronic signature requirement data into the release JSON.

    Updates or adds e-signature requirements for lots.

    Args:
        release_json: Main OCDS release JSON to update
        esignature_data: E-signature requirement data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.lots array if needed
        - Updates existing lots' submissionTerms

    """
    if not esignature_data:
        logger.warning("No electronic signature requirement data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in esignature_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            submission_terms = existing_lot.setdefault("submissionTerms", {})
            submission_terms["advancedElectronicSignatureRequired"] = new_lot[
                "submissionTerms"
            ]["advancedElectronicSignatureRequired"]
        else:
            lots.append(new_lot)

    logger.info(
        "Merged electronic signature requirement data for %d lots",
        len(esignature_data["tender"]["lots"]),
    )
