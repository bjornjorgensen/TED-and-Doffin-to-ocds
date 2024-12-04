# converters/bt_707_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}

JUSTIFICATION_MAPPING = {
    "ipr-iss": "Intellectual property right issues",
    "phy-mod": "Inclusion of a physical model",
    "sen-info": "Protection of particularly sensitive information",
    "sp-of-eq": "Buyer would need specialised office equipment",
    "tdf-non-av": "Tools, devices, or file formats not generally available",
}


def parse_part_documents_restricted_justification(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the documents restricted justification (BT-707) for procurement project parts from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed documents restricted justification data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "documents": [
                    {
                        "id": "20210521/CTFD/ENG/7654-02",
                        "accessDetails": "Intellectual property right issues"
                    }
                ]
            }
        }
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        result = {"tender": {"documents": []}}

        # Find all parts and their document references
        document_refs = root.xpath(
            """//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/
               cac:TenderingTerms/cac:CallForTendersDocumentReference""",
            namespaces=NAMESPACES,
        )

        for doc in document_refs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=NAMESPACES)
            justification = doc.xpath(
                """cbc:DocumentTypeCode[@listName='communication-justification']/
                   text()""",
                namespaces=NAMESPACES,
            )

            if doc_id and justification:
                document = {
                    "id": doc_id[0],
                    "accessDetails": JUSTIFICATION_MAPPING.get(
                        justification[0], "Unknown justification"
                    ),
                }
                result["tender"]["documents"].append(document)

        return result if result["tender"]["documents"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise


def merge_part_documents_restricted_justification(
    release_json: dict[str, Any],
    part_documents_data: dict[str, Any] | None,
) -> None:
    """Merge documents restricted justification data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        part_documents_data: The documents restricted justification data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not part_documents_data:
        logger.warning("No part documents restricted justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in part_documents_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            existing_doc["accessDetails"] = new_doc["accessDetails"]
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged part documents restricted justification data for %d documents",
        len(part_documents_data["tender"]["documents"]),
    )
