# converters/bt_615_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_documents_restricted_url(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the documents restricted URL (BT-615) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed documents restricted URL data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "documents": [
                    {
                        "id": "20210521/CTFD/ENG/7654-02",
                        "accessDetailsURL": "https://mywebsite.com/proc/2019024/accessinfo",
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

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        documents = lot.xpath(
            "cac:TenderingTerms/cac:CallForTendersDocumentReference[cbc:DocumentType/text()='restricted-document']",
            namespaces=namespaces,
        )

        for document in documents:
            doc_id = document.xpath("cbc:ID/text()", namespaces=namespaces)
            url = document.xpath(
                "cac:Attachment/cac:ExternalReference/cbc:URI/text()",
                namespaces=namespaces,
            )

            if doc_id and url:
                doc_data = {
                    "id": doc_id[0],
                    "accessDetailsURL": url[0],
                    "relatedLots": [lot_id],
                }
                result["tender"]["documents"].append(doc_data)

    return result if result["tender"]["documents"] else None


def merge_documents_restricted_url(
    release_json: dict[str, Any],
    documents_data: dict[str, Any] | None,
) -> None:
    """Merge documents restricted URL data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        documents_data: The documents restricted URL data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not documents_data:
        logger.warning("BT-615-Lot: No documents restricted URL data to merge")
        return

    existing_documents = release_json.setdefault("tender", {}).setdefault(
        "documents",
        [],
    )

    for new_doc in documents_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            existing_doc["accessDetailsURL"] = new_doc["accessDetailsURL"]
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(
                set(existing_doc["relatedLots"]),
            )  # Remove duplicates
        else:
            existing_documents.append(new_doc)

    logger.info(
        "BT-615-Lot: Merged documents restricted URL data for %d documents",
        len(documents_data["tender"]["documents"]),
    )
