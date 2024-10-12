# converters/opt_140_part_procurement_docs.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_procurement_documents_id_part(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"documents": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces
    )

    for part in parts:
        doc_refs = part.xpath(
            "cac:TenderingTerms/cac:CallForTendersDocumentReference/cbc:ID/text()",
            namespaces=namespaces,
        )

        for doc_id in doc_refs:
            result["tender"]["documents"].append({"id": doc_id})

    return result if result["tender"]["documents"] else None


def merge_procurement_documents_id_part(release_json, proc_docs_data):
    if not proc_docs_data:
        logger.info("No procurement documents ID data for parts to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in proc_docs_data["tender"]["documents"]:
        if not any(doc["id"] == new_doc["id"] for doc in existing_docs):
            existing_docs.append(new_doc)

    logger.info(
        "Merged procurement documents ID data for %d documents (parts)",
        len(proc_docs_data["tender"]["documents"]),
    )
