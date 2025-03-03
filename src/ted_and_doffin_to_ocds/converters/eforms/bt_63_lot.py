# converters/bt_63_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Mapping from eForm values to OCDS values for variants policy
# According to BT-63 and OCDS submissionTerms extension
VARIANT_POLICY_MAPPING = {
    "required": "required",
    "allowed": "allowed",
    "not-allowed": "notAllowed",
}


def parse_variants(xml_content: str | bytes) -> dict | None:
    """Parse variants policy from XML for each lot.

    Extracts whether tenderers are required, allowed, or not allowed to submit variant
    tenders as defined in BT-63 (Variants). This business term specifies whether tenderers
    can submit tenders which fulfill the buyer's needs differently than as proposed in
    the procurement documents.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "submissionTerms": {
                            "variantPolicy": str  # One of: "required", "allowed", "notAllowed"
                        }
                    }
                ]
            }
        }
        Returns None if no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.

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
    relevant_xpath = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cbc:VariantConstraintCode[@listName='permission']"
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info("No variants policy data found. Skipping parse_variants.")
        return None

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        variant_constraint = lot.xpath(
            "./cac:TenderingTerms/cbc:VariantConstraintCode[@listName='permission']/text()",
            namespaces=namespaces,
        )

        if variant_constraint:
            variant_policy = VARIANT_POLICY_MAPPING.get(variant_constraint[0])
            if variant_policy:
                lot_data = {
                    "id": lot_id,
                    "submissionTerms": {"variantPolicy": variant_policy},
                }
                result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_variants(release_json: dict, variants_data: dict | None) -> None:
    """Merge variants policy data into the OCDS release.

    Updates the release JSON in-place by adding or updating submission terms
    for each lot specified in the input data. This implements BT-63 (Variants)
    in the OCDS release according to the submissionTerms extension.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        variants_data: The parsed variants data in the same format as returned
            by parse_variants(). If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not variants_data:
        logger.info("No variants policy data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in variants_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(
                new_lot["submissionTerms"]
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged variants policy data for %d lots",
        len(variants_data["tender"]["lots"]),
    )
