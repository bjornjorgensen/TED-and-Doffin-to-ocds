import logging
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_procurement_documents_change_date(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the procurement documents change date (BT-719) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed procurement documents change date in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "documents": [
                    {
                        "dateModified": "2019-10-24T00:00:00+01:00",
                        "documentType": "biddingDocuments",
                        "relatedLots": [
                            "LOT-0001"
                        ]
                    }
                ]
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

    result = {"tender": {"documents": []}}

    changes = root.xpath(
        "//efac:Changes/efac:Change",
        namespaces=namespaces,
    )

    for change in changes:
        change_date = change.xpath(
            "efbc:ProcurementDocumentsChangeDate/text()",
            namespaces=namespaces,
        )
        if not change_date:
            continue

        # Convert date to ISO format using start_date helper
        iso_date = start_date(change_date[0])

        # Get lot identifiers if they exist
        lot_identifiers = change.xpath(
            "efac:ChangedSection/efbc:ChangedSectionIdentifier[starts-with(text(), 'LOT-')]/text()",
            namespaces=namespaces,
        )

        document = {"dateModified": iso_date, "documentType": "biddingDocuments"}

        if lot_identifiers:
            document["relatedLots"] = lot_identifiers

        result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_procurement_documents_change_date(
    release_json: dict[str, Any],
    change_date_data: dict[str, Any] | None,
) -> None:
    """Merge procurement documents change date data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        change_date_data: The procurement documents change date data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not change_date_data:
        logger.warning("No procurement documents change date data to merge")
        return

    tender_documents = release_json.setdefault("tender", {}).setdefault("documents", [])

    for new_doc in change_date_data["tender"]["documents"]:
        if "relatedLots" in new_doc:
            for lot_id in new_doc["relatedLots"]:
                existing_doc = next(
                    (
                        doc
                        for doc in tender_documents
                        if doc.get("documentType") == "biddingDocuments"
                        and lot_id in doc.get("relatedLots", [])
                    ),
                    None,
                )
                if existing_doc:
                    existing_doc["dateModified"] = new_doc["dateModified"]
                else:
                    tender_documents.append(new_doc)
        else:
            existing_doc = next(
                (
                    doc
                    for doc in tender_documents
                    if doc.get("documentType") == "biddingDocuments"
                    and "relatedLots" not in doc
                ),
                None,
            )
            if existing_doc:
                existing_doc["dateModified"] = new_doc["dateModified"]
            else:
                tender_documents.append(new_doc)

    logger.info(
        "Merged procurement documents change date data for %d documents",
        len(change_date_data["tender"]["documents"]),
    )
