# converters/bt_88_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_features(xml_content: str | bytes) -> dict | None:
    """Parse procedure features from XML.

    Extract information about the main features of the procedure and references to
    where the full rules can be found as defined in BT-88.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "procurementMethodDetails": str
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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    procedure_features = root.xpath(
        "//cac:TenderingProcess/cbc:Description/text()",
        namespaces=namespaces,
    )

    if procedure_features:
        return {"tender": {"procurementMethodDetails": procedure_features[0]}}

    return None


def merge_procedure_features(
    release_json: dict, procedure_features_data: dict | None
) -> None:
    """Merge procedure features data into the OCDS release.

    Updates the release JSON in-place by adding or updating procurement method details.

    Args:
        release_json: The main OCDS release JSON to be updated.
        procedure_features_data: The parsed procedure features data
            in the same format as returned by parse_procedure_features().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.

    """
    if not procedure_features_data:
        logger.warning("No procedure features data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender["procurementMethodDetails"] = procedure_features_data["tender"][
        "procurementMethodDetails"
    ]

    logger.info("Merged procedure features data")
