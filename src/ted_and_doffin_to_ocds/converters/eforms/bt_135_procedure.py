# converters/bt_135_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_direct_award_justification_rationale(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the direct award justification rationale from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing justification information

    Returns:
        Optional[Dict]: Dictionary containing tender information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "procurementMethodRationale": str
            }
        }

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

    reasons = root.xpath(
        "/*/cac:TenderingProcess/cac:ProcessJustification"
        "[cbc:ProcessReasonCode/@listName='direct-award-justification']"
        "/cbc:ProcessReason/text()",
        namespaces=namespaces,
    )

    if reasons:
        rationale = " ".join(reason.strip() for reason in reasons if reason.strip())
        return {"tender": {"procurementMethodRationale": rationale}}

    return None


def merge_direct_award_justification_rationale(
    release_json: dict, justification_data: dict | None
) -> None:
    """Merge direct award justification rationale into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        justification_data (Optional[Dict]): The source data containing justification
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.procurementMethodRationale field.

    """
    if not justification_data:
        return

    tender = release_json.setdefault("tender", {})
    tender["procurementMethodRationale"] = justification_data["tender"][
        "procurementMethodRationale"
    ]
    logger.info("Merged direct award justification rationale")
