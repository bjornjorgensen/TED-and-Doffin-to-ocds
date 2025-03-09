# converters/bt_17_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_submission_electronic(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse electronic submission policy for each lot from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing lots data with submission policies,
                                 or None if no valid data is found

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

    # Map of XML submission values to OCDS permission codelist values
    # Based on the eForms permission codelist values
    submission_policy_map = {
        "required": "required",
        "allowed": "allowed",
        "notAllowed": "notAllowed",
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        submission_method = lot.xpath(
            "cac:TenderingProcess/cbc:SubmissionMethodCode[@listName='esubmission']/text()",
            namespaces=namespaces,
        )

        if lot_id and submission_method:
            policy_value = submission_method[0]
            # Map to standard permission codelist value, defaulting to original if not in map
            policy_value = submission_policy_map.get(policy_value, policy_value)

            lot_data = {
                "id": lot_id[0],
                "submissionTerms": {"electronicSubmissionPolicy": policy_value},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_submission_electronic(
    release_json: dict[str, Any], submission_electronic_data: dict[str, Any] | None
) -> None:
    """Merge electronic submission policy data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        submission_electronic_data (Optional[Dict[str, Any]]): Lot data containing submission policies to merge

    """
    if not submission_electronic_data:
        logger.warning("No Submission Electronic data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in submission_electronic_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(
                new_lot["submissionTerms"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Submission Electronic data for %d lots",
        len(submission_electronic_data["tender"]["lots"]),
    )
